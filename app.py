from flask import Flask, render_template, request, jsonify
import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__, static_folder='static')

MY_API_KEY = ""
HEADERS = {"Authorization": MY_API_KEY}

AGENTS_CN = {
    "Jett": "捷风", "Reyna": "瑞纳", "Raze": "雷兹", "Neon": "霓虹", "Phoenix": "不死鸟",
    "Yoru": "夜露", "Sage": "贤者", "Skye": "斯凯", "Sova": "猎枭", "Breach": "铁臂",
    "Omen": "幽影", "Brimstone": "炼狱", "Viper": "蝰蛇", "Killjoy": "奇乐", "Cypher": "零",
    "Chamber": "尚勃勒", "Fade": "黑梦", "KAY/O": "K/O", "Astra": "星礈", "Harbor": "海神",
    "Gekko": "盖克", "Deadlock": "钢索", "Iso": "壹决", "Clove": "暮蝶", "Vyse": "维斯"
}

# 已更新为官方译名
MAPS_CN = {
    "Bind": "源工重镇",
    "Haven": "隐世修所",
    "Split": "霓虹町",
    "Ascent": "亚海悬城",
    "Icebox": "森寒冬港",
    "Breeze": "微风岛屿",
    "Fracture": "裂变峡谷",
    "Pearl": "深海明珠",
    "Lotus": "莲华古城",
    "Sunset": "日落之城",
    "Abyss": "幽邃地窟",
    "District": "区域", "Kasbah": "古堡", "Piazza": "广场", "Drift": "漂浮", "Basic Training": "基础训练"
}

MODES_CN = {
    "Competitive": "竞技模式", "Unrated": "一般模式", "Swiftplay": "极速模式",
    "Deathmatch": "死斗模式", "Team Deathmatch": "团队死斗", "Spike Rush": "乱斗模式"
}


class ValorantProAnalyzer:
    def __init__(self, name, tag, region='ap'):
        self.name, self.tag, self.region = name, tag, region

    def fetch_all(self):
        with ThreadPoolExecutor(max_workers=3) as ex:
            f_acc = ex.submit(self._get, f"https://api.henrikdev.xyz/valorant/v1/account/{self.name}/{self.tag}")
            f_mmr = ex.submit(self._get,
                              f"https://api.henrikdev.xyz/valorant/v2/mmr/{self.region}/{self.name}/{self.tag}")
            f_matches = ex.submit(self._get,
                                  f"https://api.henrikdev.xyz/valorant/v3/matches/{self.region}/{self.name}/{self.tag}?size=20")
        return f_acc.result(), f_mmr.result(), f_matches.result()

    def _get(self, url):
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            return r.json().get('data') if r.status_code == 200 else None
        except:
            return None

    def analyze(self, acc, mmr, matches):
        if not matches: return None
        target_id = f"{self.name.lower()}#{self.tag.lower()}"
        all_history = []
        std_list = []
        STANDARD_MODES = ['Competitive', 'Unrated', 'Swiftplay']

        for m in matches:
            if not m or not isinstance(m, dict): continue
            meta = m.get('metadata', {})
            players = m.get('players', {}).get('all_players', [])
            rounds = meta.get('rounds_played', 1) or 1
            raw_mode = meta.get('mode', '')

            all_pl_data = []
            for pl in players:
                ps = pl.get('stats', {})
                pac = round(ps.get('score', 0) / rounds)
                phs, pbs, pls = ps.get('headshots', 0), ps.get('bodyshots', 0), ps.get('legshots', 0)
                ptot = phs + pbs + pls
                phs_rate = f"{round(phs / ptot * 100)}%" if ptot > 0 else "0%"

                all_pl_data.append({
                    "name": pl.get('name'), "tag": pl.get('tag'),
                    "team": "红队" if pl.get('team').lower() == 'red' else "蓝队",
                    "agent": AGENTS_CN.get(pl.get('character'), pl.get('character')),
                    "agent_img": pl.get('assets', {}).get('agent', {}).get('small'),
                    "rank_img": f"https://media.valorant-api.com/competitivetiers/03621d13-43b4-d6ef-20fd-2e8648b292e2/{pl.get('currenttier', 0)}/smallicon.png",
                    "kda": f"{ps.get('kills')}-{ps.get('deaths')}-{ps.get('assists')}",
                    "acs": pac,
                    "hs_rate": phs_rate
                })

            p = next((x for x in players if f"{x.get('name', '').lower()}#{x.get('tag', '').lower()}" == target_id),
                     None)
            if not p: continue

            p_stats = p.get('stats', {})
            hs, bs, ls = p_stats.get('headshots', 0), p_stats.get('bodyshots', 0), p_stats.get('legshots', 0)
            hs_rate = round(hs / (hs + bs + ls) * 100, 1) if (hs + bs + ls) > 0 else 0
            my_acs = round(p_stats.get('score', 0) / rounds)
            kills, deaths = p_stats.get('kills', 0), p_stats.get('deaths', 0)
            kd_ratio = round(kills / deaths, 2) if deaths > 0 else kills

            teams = m.get('teams', {})
            my_team = p.get('team', '').lower()
            if raw_mode == 'Deathmatch':
                res_cn = "胜利" if kills >= 40 else "完成"
                score_str = str(kills)
            else:
                res_cn = "胜利" if teams.get(my_team, {}).get('has_won') else "失败"
                if teams.get('red', {}).get('rounds_won') == teams.get('blue', {}).get('rounds_won'): res_cn = "平局"
                score_str = f"{teams.get(my_team, {}).get('rounds_won', 0)} : {teams.get('blue' if my_team == 'red' else 'red', {}).get('rounds_won', 0)}"

            match_info = {
                "mode": MODES_CN.get(raw_mode, raw_mode),
                "map": MAPS_CN.get(meta.get('map'), meta.get('map')),
                "agent": AGENTS_CN.get(p.get('character'), p.get('character')),
                "agent_img": p.get('assets', {}).get('agent', {}).get('small'),
                "result": res_cn,
                "score": score_str,
                "acs": my_acs,
                "kd_ratio": kd_ratio,
                "adr": round(p.get('damage_made', 0) / rounds, 1),
                "hs": hs_rate,
                "kda": f"{kills}/{deaths}/{p_stats.get('assists', 0)}",
                "is_mvp": my_acs >= (max([pl['acs'] for pl in all_pl_data]) if all_pl_data else 0),
                "timestamp": meta.get('game_start', 0),
                "all_players": all_pl_data
            }
            all_history.append(match_info)
            if raw_mode in STANDARD_MODES: std_list.append(match_info)

        df = pd.DataFrame(std_list) if std_list else pd.DataFrame()

        # 增加默认图片防止 null 404
        def_avatar = "https://media.valorant-api.com/playercards/2316e6ef-466c-3837-1473-b79e4368551a/smallicon.png"

        return {
            "profile": {
                "level": acc.get('account_level') if acc else "?",
                "card": acc.get('card', {}).get('wide', "") if acc else "",
                "avatar": acc.get('card', {}).get('small', def_avatar) if acc else def_avatar,
                "rank_label": mmr.get('current_data', {}).get('currenttierpatched', '未定级') if mmr else "未定级",
                "rank_img": mmr.get('current_data', {}).get('images', {}).get('small', "") if mmr else ""
            },
            "stats": {
                "total": len(all_history),
                "wr": f"{round(len(df[df['result'] == '胜利']) / len(df) * 100)}%" if not df.empty else "0%",
                "acs": int(df['acs'].mean()) if not df.empty else 0,
                "adr": round(df['adr'].mean(), 1) if not df.empty else 0,
                "kd": round(df['kd_ratio'].mean(), 2) if not df.empty else 0,
                "hs": f"{round(df['hs'].mean(), 1)}%" if not df.empty else "0%"
            },
            "charts": {
                "labels": [f"M{i + 1}" for i in range(len(df))][::-1],
                "acs": df['acs'].tolist()[::-1],
                "hs": df['hs'].tolist()[::-1]
            },
            "history": all_history
        }


@app.route('/')
def index(): return render_template('index.html')


@app.route('/api/analyze', methods=['POST'])
def run():
    req = request.json
    az = ValorantProAnalyzer(req['name'], req['tag'], req['region'])
    acc, mmr, matches = az.fetch_all()
    res = az.analyze(acc, mmr, matches)
    return jsonify({"status": "success", "data": res}) if res else jsonify({"status": "error"})


if __name__ == '__main__':
    app.run(debug=True)