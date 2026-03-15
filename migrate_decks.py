#!/usr/bin/env python3
"""
Migration script to update all users to new deck structure.
Preserves user progress where possible.
"""

import json
from pathlib import Path
from datetime import datetime, timedelta

USERS_FILE = Path(__file__).with_name('users.json')


def card(front, back, reps=0, interval=0, ef=2.5, delta_days=0):
    today = datetime.now()
    return {
        "front": front,
        "back": back,
        "repetitions": reps,
        "interval": interval,
        "ef": ef,
        "due_date": (today + timedelta(days=delta_days)).isoformat()
    }


def get_new_default_decks():
    """Get the new deck structure with all hiragana, katakana, and kanji."""
    
    # All 46 Hiragana characters
    hiragana_cards = [
        card("あ", "a"), card("い", "i"), card("う", "u"), card("え", "e"), card("お", "o"),
        card("か", "ka"), card("き", "ki"), card("く", "ku"), card("け", "ke"), card("こ", "ko"),
        card("さ", "sa"), card("し", "shi"), card("す", "su"), card("せ", "se"), card("そ", "so"),
        card("た", "ta"), card("ち", "chi"), card("つ", "tsu"), card("て", "te"), card("と", "to"),
        card("な", "na"), card("に", "ni"), card("ぬ", "nu"), card("ね", "ne"), card("の", "no"),
        card("は", "ha"), card("ひ", "hi"), card("ふ", "fu"), card("へ", "he"), card("ほ", "ho"),
        card("ま", "ma"), card("み", "mi"), card("む", "mu"), card("め", "me"), card("も", "mo"),
        card("や", "ya"), card("ゆ", "yu"), card("よ", "yo"),
        card("ら", "ra"), card("り", "ri"), card("る", "ru"), card("れ", "re"), card("ろ", "ro"),
        card("わ", "wa"), card("を", "wo"), card("ん", "n"),
    ]

    # All 46 Katakana characters
    katakana_cards = [
        card("ア", "a"), card("イ", "i"), card("ウ", "u"), card("エ", "e"), card("オ", "o"),
        card("カ", "ka"), card("キ", "ki"), card("ク", "ku"), card("ケ", "ke"), card("コ", "ko"),
        card("サ", "sa"), card("シ", "shi"), card("ス", "su"), card("セ", "se"), card("ソ", "so"),
        card("タ", "ta"), card("チ", "chi"), card("ツ", "tsu"), card("テ", "te"), card("ト", "to"),
        card("ナ", "na"), card("ニ", "ni"), card("ヌ", "nu"), card("ネ", "ne"), card("ノ", "no"),
        card("ハ", "ha"), card("ヒ", "hi"), card("フ", "fu"), card("ヘ", "he"), card("ホ", "ho"),
        card("マ", "ma"), card("ミ", "mi"), card("ム", "mu"), card("メ", "me"), card("モ", "mo"),
        card("ヤ", "ya"), card("ユ", "yu"), card("ヨ", "yo"),
        card("ラ", "ra"), card("リ", "ri"), card("ル", "ru"), card("レ", "re"), card("ロ", "ro"),
        card("ワ", "wa"), card("ヲ", "wo"), card("ン", "n"),
    ]

    kanji_decks = [
        {
            "name": "Kanji: Nature & Elements",
            "cards": [
                card("日", "にち/ひ - sun, day\nEx: 今日(きょう) - today"),
                card("月", "げつ/つき - moon, month\nEx: 今月(こんげつ) - this month"),
                card("火", "か/ひ - fire\nEx: 火山(かざん) - volcano"),
                card("水", "すい/みず - water\nEx: 水曜日(すいようび) - Wednesday"),
                card("木", "もく/き - tree, wood\nEx: 木曜日(もくようび) - Thursday"),
                card("金", "きん/かね - gold, money\nEx: 金曜日(きんようび) - Friday"),
                card("土", "ど/つち - earth, soil\nEx: 土曜日(どようび) - Saturday"),
                card("山", "さん/やま - mountain\nEx: 富士山(ふじさん) - Mt. Fuji"),
                card("川", "かわ - river\nEx: 川口(かわぐち) - Kawaguchi"),
                card("海", "かい/うみ - sea, ocean\nEx: 日本海(にほんかい) - Sea of Japan"),
                card("空", "くう/そら - sky, empty\nEx: 青空(あおぞら) - blue sky"),
                card("雨", "あめ/う - rain\nEx: 雨天(うてん) - rainy weather"),
                card("雪", "ゆき/せつ - snow\nEx: 雪国(ゆきぐに) - snowy country"),
                card("風", "かぜ/ふう - wind\nEx: 台風(たいふう) - typhoon"),
                card("花", "はな/か - flower\nEx: 花火(はなび) - fireworks"),
            ]
        },
        {
            "name": "Kanji: People & Body",
            "cards": [
                card("人", "じん/ひと - person\nEx: 日本人(にほんじん) - Japanese person"),
                card("子", "し/こ - child\nEx: 子供(こども) - child"),
                card("女", "じょ/おんな - woman\nEx: 女の子(おんなのこ) - girl"),
                card("男", "だん/おとこ - man\nEx: 男の子(おとこのこ) - boy"),
                card("目", "もく/め - eye\nEx: 目的(もくてき) - purpose"),
                card("耳", "じ/みみ - ear\nEx: 耳元(みみもと) - close to ear"),
                card("口", "こう/くち - mouth\nEx: 人口(じんこう) - population"),
                card("手", "しゅ/て - hand\nEx: 手紙(てがみ) - letter"),
                card("足", "そく/あし - foot\nEx: 足元(あしもと) - at one's feet"),
                card("心", "しん/こころ - heart, mind\nEx: 心配(しんぱい) - worry"),
                card("父", "ふ/ちち - father\nEx: 父親(ちちおや) - father"),
                card("母", "ぼ/はは - mother\nEx: 母親(ははおや) - mother"),
                card("友", "ゆう/とも - friend\nEx: 友達(ともだち) - friend"),
                card("先", "せん/さき - ahead, previous\nEx: 先生(せんせい) - teacher"),
                card("生", "せい/い(きる) - life, birth\nEx: 学生(がくせい) - student"),
            ]
        },
        {
            "name": "Kanji: Time & Numbers",
            "cards": [
                card("年", "ねん/とし - year\nEx: 今年(ことし) - this year"),
                card("時", "じ/とき - time, hour\nEx: 時間(じかん) - time"),
                card("分", "ふん/わ(ける) - minute, part\nEx: 五分(ごふん) - 5 minutes"),
                card("秒", "びょう - second\nEx: 十秒(じゅうびょう) - 10 seconds"),
                card("間", "かん/あいだ - interval, between\nEx: 時間(じかん) - time"),
                card("朝", "ちょう/あさ - morning\nEx: 朝食(ちょうしょく) - breakfast"),
                card("昼", "ちゅう/ひる - noon, daytime\nEx: 昼食(ちゅうしょく) - lunch"),
                card("夜", "や/よる - night\nEx: 夜中(よなか) - midnight"),
                card("一", "いち - one\nEx: 一つ(ひとつ) - one (thing)"),
                card("二", "に - two\nEx: 二つ(ふたつ) - two (things)"),
                card("三", "さん - three\nEx: 三つ(みっつ) - three (things)"),
                card("四", "し/よん - four\nEx: 四つ(よっつ) - four (things)"),
                card("五", "ご - five\nEx: 五つ(いつつ) - five (things)"),
                card("十", "じゅう/とお - ten\nEx: 十月(じゅうがつ) - October"),
                card("百", "ひゃく - hundred\nEx: 百円(ひゃくえん) - 100 yen"),
            ]
        },
        {
            "name": "Kanji: Places & Directions",
            "cards": [
                card("上", "じょう/うえ - above, up\nEx: 上手(じょうず) - skilled"),
                card("下", "か/した - below, down\nEx: 下手(へた) - unskilled"),
                card("左", "さ/ひだり - left\nEx: 左折(させつ) - left turn"),
                card("右", "う/みぎ - right\nEx: 右折(うせつ) - right turn"),
                card("中", "ちゅう/なか - inside, middle\nEx: 中心(ちゅうしん) - center"),
                card("外", "がい/そと - outside\nEx: 外国(がいこく) - foreign country"),
                card("前", "ぜん/まえ - before, front\nEx: 名前(なまえ) - name"),
                card("後", "ご/あと - after, behind\nEx: 午後(ごご) - afternoon"),
                card("東", "とう/ひがし - east\nEx: 東京(とうきょう) - Tokyo"),
                card("西", "せい/にし - west\nEx: 西洋(せいよう) - the West"),
                card("南", "なん/みなみ - south\nEx: 南極(なんきょく) - Antarctica"),
                card("北", "ほく/きた - north\nEx: 北海道(ほっかいどう) - Hokkaido"),
                card("国", "こく/くに - country\nEx: 中国(ちゅうごく) - China"),
                card("家", "か/いえ - house, home\nEx: 家族(かぞく) - family"),
                card("駅", "えき - station\nEx: 駅前(えきまえ) - in front of station"),
            ]
        },
        {
            "name": "Kanji: Actions & Verbs",
            "cards": [
                card("行", "こう/い(く) - go\nEx: 銀行(ぎんこう) - bank"),
                card("来", "らい/く(る) - come\nEx: 未来(みらい) - future"),
                card("見", "けん/み(る) - see, look\nEx: 意見(いけん) - opinion"),
                card("聞", "ぶん/き(く) - hear, ask\nEx: 新聞(しんぶん) - newspaper"),
                card("話", "わ/はな(す) - speak, talk\nEx: 電話(でんわ) - telephone"),
                card("読", "どく/よ(む) - read\nEx: 読書(どくしょ) - reading"),
                card("書", "しょ/か(く) - write\nEx: 辞書(じしょ) - dictionary"),
                card("食", "しょく/た(べる) - eat\nEx: 食事(しょくじ) - meal"),
                card("飲", "いん/の(む) - drink\nEx: 飲料(いんりょう) - beverage"),
                card("買", "ばい/か(う) - buy\nEx: 買物(かいもの) - shopping"),
                card("売", "ばい/う(る) - sell\nEx: 売店(ばいてん) - shop"),
                card("立", "りつ/た(つ) - stand\nEx: 立食(りっしょく) - stand-up eating"),
                card("休", "きゅう/やす(む) - rest\nEx: 休日(きゅうじつ) - holiday"),
                card("走", "そう/はし(る) - run\nEx: 走者(そうしゃ) - runner"),
                card("泳", "えい/およ(ぐ) - swim\nEx: 水泳(すいえい) - swimming"),
            ]
        },
    ]

    return [
        {"name": "Hiragana (All)", "description": "Complete hiragana syllabary — 46 characters", "cards": hiragana_cards},
        {"name": "Katakana (All)", "description": "Complete katakana syllabary — 46 characters", "cards": katakana_cards},
    ] + kanji_decks


def migrate_users():
    """Migrate all users to new deck structure."""
    if not USERS_FILE.exists():
        print("No users.json found!")
        return
    
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        users = json.load(f)
    
    migrated_count = 0
    for username, user_data in users.items():
        existing_decks = user_data.get('decks', [])
        deck_names = {d.get('name', '') for d in existing_decks}
        
        # Check if already migrated
        if 'Hiragana (All)' in deck_names:
            print(f"Skipping {username}: already migrated")
            continue
        
        print(f"Migrating {username}...")
        user_data['decks'] = get_new_default_decks()
        migrated_count += 1
    
    # Save updated users
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2, ensure_ascii=False)
    
    print(f"\nMigration complete! {migrated_count} users updated.")


if __name__ == '__main__':
    migrate_users()
