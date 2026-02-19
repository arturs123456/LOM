#!/usr/bin/env python3
"""
Assign genre categories to Latvian MTV songs.
Goal: each song should have at least 2 categories marked with "X".

Time-period rules (strictly by year):
  RETRO:   year <= 1987
  ATMODA:  year 1988-1995
  JAUNUMI: year >= 2022
  (1996-2021: no time-period — need 2 style categories)

For the 1996-2021 "gap" songs, we assign multiple style categories using
artist knowledge rather than forcing LĀGERIS on pop-rock bands.
"""

import csv
from collections import Counter

INPUT_FILE = '/Users/arturs25/Desktop/ATVERTS FINAL/latvijas-mtv-v2/sheets_full_import.csv'
OUTPUT_FILE = '/Users/arturs25/Desktop/ATVERTS FINAL/latvijas-mtv-v2/sheets_import_genres.tsv'

COL_YOUTUBE = 0; COL_ARTIST = 1; COL_SONG = 2; COL_ALBUM = 3
COL_YEAR = 4; COL_LENGTH = 5; COL_ERA = 6
COL_TRIM_START = 7; COL_TRIM_END = 8

GENRE_START = 9
GENRE_NAMES = [
    'POP', 'SMAGAIS ROKS', 'LĀGERIS', 'RETRO', 'RZEMJU', 'ATMODA',
    'JAUNUMI', 'HIPHOP', 'DZIESMU ŠOV', 'LIVE', 'BĒRNU', 'JAZZ',
    'DEJU MŪZIKA', 'ELECTRO', 'FOLK', 'REĢEJS', 'Akadēmiskā',
]

TIME_PERIOD_CATS = {'RETRO', 'ATMODA', 'JAUNUMI'}
STYLE_CATS = set(GENRE_NAMES) - TIME_PERIOD_CATS

# ─── Artist → genre mapping ──────────────────────────────────────────────
# Each artist gets ALL applicable style genres (ideally 2+ for 1996-2021 artists)
# Keys are fuzzy-matched (case-insensitive substring)

artist_genres = {
    # ═══════════════════════════════════════════════════════════════════════
    # ŠLĀGERIS / EASY LISTENING (vintage era singers & ensembles)
    # ═══════════════════════════════════════════════════════════════════════
    'Nora Bumbiere': ['LĀGERIS', 'POP'],
    'N. Bumbiere': ['LĀGERIS', 'POP'],
    'Viktors Lapčenoks': ['LĀGERIS', 'POP'],
    'V. Lapčenoks': ['LĀGERIS', 'POP'],
    'Menuets': ['LĀGERIS', 'POP'],
    'Jānis Paukštello': ['LĀGERIS', 'POP'],
    'Ēriks Kamarūts': ['LĀGERIS', 'POP'],
    'Aija Kukule': ['LĀGERIS', 'POP'],
    'Margarita Vilcāne': ['LĀGERIS', 'POP'],
    'M. Vilcāne': ['LĀGERIS', 'POP'],
    'Ojārs Grinbergs': ['LĀGERIS', 'POP'],
    'O. Grinbergs': ['LĀGERIS', 'POP'],
    'Uldis Stabulnieks': ['LĀGERIS', 'POP'],
    'Imants Skrastiņš': ['LĀGERIS', 'POP'],
    'Sandra Ozolīte': ['LĀGERIS', 'POP'],
    'Sandra Ozoliņa': ['LĀGERIS', 'POP'],
    'Uldis Dumpis': ['LĀGERIS', 'POP'],
    'Ingus Pētersons': ['LĀGERIS', 'POP'],
    'Mirdza Zīvere': ['LĀGERIS', 'POP'],
    'Eolika': ['LĀGERIS', 'POP'],
    'Andris Sējāns': ['LĀGERIS', 'POP'],
    'Čikāgas Piecīši': ['LĀGERIS', 'POP'],
    'Imants Kalniņš': ['LĀGERIS', 'POP'],
    'Zigmars Liepiņš': ['LĀGERIS', 'POP'],
    'Z. Liepiņš': ['LĀGERIS', 'POP'],
    'Gunārs Kalniņš': ['LĀGERIS', 'POP'],
    'Gunārs Placēns': ['LĀGERIS', 'POP'],
    'Ārija Elksne': ['LĀGERIS', 'POP'],
    'Nikolajs Puzikovs': ['LĀGERIS', 'POP'],
    'Žoržs Siksna': ['LĀGERIS', 'POP'],
    'Andris Ērglis': ['LĀGERIS', 'POP'],
    'Edgars Liepiņš': ['LĀGERIS', 'POP'],
    'Uldis Marhilevičs': ['LĀGERIS', 'POP'],
    'Imants Vanzovičs': ['LĀGERIS', 'POP'],
    'Adrians Kukuvass': ['LĀGERIS', 'POP'],
    'REO': ['LĀGERIS', 'POP'],
    'Varavīksne': ['LĀGERIS', 'POP'],
    'Liepājas brāļi': ['LĀGERIS', 'POP'],
    'Aktieru ansamblis': ['LĀGERIS', 'POP'],
    'Andrejs Lihtenbergs': ['LĀGERIS', 'POP'],
    'K. Dimiters': ['LĀGERIS', 'POP'],
    'L. Pere': ['LĀGERIS', 'POP'],
    'Cacao': ['LĀGERIS', 'POP'],
    'Raimonds Pauls': ['JAZZ', 'LĀGERIS'],
    'R.Pauls': ['JAZZ', 'LĀGERIS'],

    # ═══════════════════════════════════════════════════════════════════════
    # POP / POP-ROCK (90s-2020s mainstream Latvian pop)
    # For 1996-2021 artists, we assign 2 styles: POP + a secondary
    # ═══════════════════════════════════════════════════════════════════════

    # Pop-rock bands (POP + secondary style)
    'Prāta Vētra': ['POP', 'SMAGAIS ROKS'],  # pop-rock band
    'BrainStorm': ['POP', 'SMAGAIS ROKS'],
    'Jumprava': ['POP', 'LĀGERIS'],  # nostalgic pop, schlager-adjacent
    'Opus Pro': ['POP', 'LĀGERIS'],  # classic Latvian pop
    'Opus': ['POP', 'LĀGERIS'],
    'Credo': ['POP', 'LĀGERIS'],     # pop with schlager roots
    'Līvi': ['POP', 'LĀGERIS'],      # Special-cased for vintage in code
    'Remix': ['POP', 'LĀGERIS'],     # 80s-90s pop group
    'Igo': ['POP', 'LĀGERIS'],       # classic crooner pop

    # Pure pop / dance-pop artists
    'Labvēlīgais Tips': ['POP', 'SMAGAIS ROKS'],  # energetic pop-rock
    'Bet Bet': ['POP', 'SMAGAIS ROKS'],            # pop-rock/punk-pop
    'Instrumenti': ['POP', 'ELECTRO'],              # indie-pop/electronic
    'Musiqq': ['POP', 'ELECTRO'],                   # modern pop/RnB
    'Dons': ['POP', 'HIPHOP'],                      # pop with hip-hop influence
    'Intars Busulis': ['POP', 'JAZZ'],               # pop with jazz vocals
    'Lauris Reiniks': ['POP', 'DEJU MŪZIKA'],       # dance-pop
    'Aminata': ['POP', 'ELECTRO'],
    'Samanta Tīna': ['POP', 'DEJU MŪZIKA'],
    'Ralfs Eilands': ['POP', 'SMAGAIS ROKS'],       # Citi Zēni frontman
    'Sudden Lights': ['POP', 'SMAGAIS ROKS'],       # indie-rock
    "Astro'n'out": ['POP', 'ELECTRO'],
    'Carousel': ['POP', 'FOLK'],
    'Bermudu Divstūris': ['POP', 'HIPHOP'],         # pop with rap elements
    'Aarzemnieki': ['POP', 'FOLK'],
    'Triana Park': ['POP', 'ELECTRO'],
    'Markus Riva': ['POP', 'DEJU MŪZIKA'],
    'The Sound Poets': ['POP', 'SMAGAIS ROKS'],     # pop-rock
    'Ivo Fomins': ['POP', 'SMAGAIS ROKS'],          # pop-rock
    'Fomins': ['POP', 'SMAGAIS ROKS'],
    'Carnival Youth': ['POP', 'SMAGAIS ROKS'],      # indie-rock
    'Aija Andrejeva': ['POP', 'JAZZ'],               # jazz-pop vocalist
    'Rassell': ['POP', 'HIPHOP'],                    # pop/hip-hop
    'Jānis Stībelis': ['POP', 'FOLK'],              # singer-songwriter/folk
    'Detlef': ['POP', 'ELECTRO'],
    'Chris Noah': ['POP', 'ELECTRO'],
    'Marija Naumova': ['POP', 'JAZZ'],               # Eurovision winner, jazz-pop
    'Nicol': ['POP', 'DEJU MŪZIKA'],
    'Aisha': ['POP', 'ELECTRO'],
    'Justs': ['POP', 'ELECTRO'],
    'Pirates of the Sea': ['POP', 'SMAGAIS ROKS'],  # rock-parody
    'Jauns Mēness': ['POP', 'SMAGAIS ROKS'],        # pop-rock
    'Valters un Kaža': ['POP', 'DEJU MŪZIKA'],
    'Kaža': ['POP', 'DEJU MŪZIKA'],
    'Bonaparti': ['POP', 'ELECTRO'],
    'Logo': ['POP', 'SMAGAIS ROKS'],                # rock/pop-rock
    'The Hobos': ['POP', 'SMAGAIS ROKS'],            # rock
    'Ieva Akuratere': ['POP', 'SMAGAIS ROKS'],      # rock vocalist
    'Carnival Youth': ['POP', 'SMAGAIS ROKS'],
    'Mēnessputni': ['POP', 'SMAGAIS ROKS'],         # rock
    'Dzeltenie Pastnieki': ['POP', 'SMAGAIS ROKS'],  # punk-rock
    'Citi Zēni': ['POP', 'SMAGAIS ROKS'],
    '100. Debija': ['POP', 'SMAGAIS ROKS'],         # alt-rock
    'Tranzīts': ['POP', 'SMAGAIS ROKS'],            # rock
    'Pienvedēja Piedzīvojumi': ['POP', 'SMAGAIS ROKS'], # alt-rock
    '2xBBM': ['POP', 'SMAGAIS ROKS'],
    'Apvedceļš': ['POP', 'SMAGAIS ROKS'],           # rock
    'Putnu Balle': ['POP', 'SMAGAIS ROKS'],
    'Linga': ['POP', 'HIPHOP'],                     # pop/hip-hop
    'Fiņķis': ['POP', 'HIPHOP'],                    # pop/hip-hop
    'Gacho': ['POP', 'HIPHOP'],                     # pop/hip-hop
    'Gustavo': ['POP', 'HIPHOP'],

    # Artists that are just POP (need secondary from era if no time-period)
    'Sestā Jūdze': ['POP', 'SMAGAIS ROKS'],
    '6. jūdze': ['POP', 'SMAGAIS ROKS'],
    'Edavārdi': ['POP', 'FOLK'],
    'Agnese Rakovska': ['POP', 'JAZZ'],
    'Jenny May': ['POP', 'DEJU MŪZIKA'],
    'Antra Stafecka': ['POP', 'JAZZ'],
    'Roberts Gobziņš': ['POP', 'SMAGAIS ROKS'],
    'Mārtiņš Brauns': ['POP', 'SMAGAIS ROKS'],
    'Patrisha': ['POP', 'DEJU MŪZIKA'],
    'Ance Krauze': ['POP', 'JAZZ'],
    'Mesa': ['POP', 'ELECTRO'],
    'Rebel': ['POP', 'SMAGAIS ROKS'],
    'Shipsea': ['POP', 'ELECTRO'],
    'Agnese': ['POP', 'JAZZ'],
    'Tautas balss': ['POP', 'DEJU MŪZIKA'],
    'Otra Puse': ['POP', 'SMAGAIS ROKS'],
    'F.L.Y.': ['POP', 'ELECTRO'],
    'Jana Key': ['POP', 'DEJU MŪZIKA'],
    'Mazais Princis': ['POP', 'HIPHOP'],
    'A-Eiropa': ['POP', 'ELECTRO'],
    'Odis': ['POP', 'SMAGAIS ROKS'],
    'H2O': ['POP', 'SMAGAIS ROKS'],
    'Gain Fast': ['POP', 'SMAGAIS ROKS'],
    'K.I.N.': ['POP', 'ELECTRO'],
    'Rīgas Modes': ['POP', 'ELECTRO'],
    'Dakota': ['POP', 'SMAGAIS ROKS'],
    'Cikādes': ['POP', 'SMAGAIS ROKS'],
    'Efeja': ['POP', 'SMAGAIS ROKS'],
    'New York': ['POP', 'SMAGAIS ROKS'],
    'Cirks': ['POP', 'SMAGAIS ROKS'],
    'K.D.A.K.': ['POP', 'SMAGAIS ROKS'],
    'Huskvarn': ['POP', 'SMAGAIS ROKS'],
    'Turaidas Roze': ['POP', 'FOLK'],
    'The Satellites': ['POP', 'SMAGAIS ROKS'],
    'Ainars Mielavs': ['POP', 'SMAGAIS ROKS'],
    'Dzeguzīte': ['POP', 'FOLK'],
    'Kaimiņi': ['POP', 'SMAGAIS ROKS'],
    'Sīpoli': ['POP', 'SMAGAIS ROKS'],
    'Arnis Mednis': ['POP', 'SMAGAIS ROKS'],
    'Klaidonis': ['POP', 'SMAGAIS ROKS'],
    'Būū': ['POP', 'ELECTRO'],
    'Aigars Grāvers': ['POP', 'LĀGERIS'],
    'Olga Rajecka': ['POP', 'JAZZ'],
    'Mežs': ['POP', 'SMAGAIS ROKS'],
    'Cosmos': ['POP', 'ELECTRO'],
    'Rīgas Deju Klubs': ['DEJU MŪZIKA', 'POP'],
    'Kopkoris': ['Akadēmiskā', 'POP'],

    # ═══════════════════════════════════════════════════════════════════════
    # ROCK / HEAVY / ALTERNATIVE
    # ═══════════════════════════════════════════════════════════════════════
    'Pērkons': ['SMAGAIS ROKS', 'POP'],
    'Tumsa': ['SMAGAIS ROKS', 'POP'],
    'Dzelzs Vilks': ['SMAGAIS ROKS', 'POP'],
    'Double Faced Eels': ['SMAGAIS ROKS', 'POP'],
    'Autobuss Debesīs': ['SMAGAIS ROKS', 'POP'],
    'Skyforger': ['SMAGAIS ROKS', 'FOLK'],
    'Z-Scars': ['SMAGAIS ROKS', 'POP'],
    'Hospitāļu iela': ['SMAGAIS ROKS', 'POP'],
    'HMP?': ['SMAGAIS ROKS', 'POP'],

    # ═══════════════════════════════════════════════════════════════════════
    # HIPHOP / RAP
    # ═══════════════════════════════════════════════════════════════════════
    'Ozols': ['HIPHOP', 'POP'],
    'Ansis': ['HIPHOP', 'POP'],
    'ansis': ['HIPHOP', 'POP'],
    'Skutelis': ['HIPHOP', 'POP'],
    'R.A.P.': ['HIPHOP', 'POP'],
    'Borowa MC': ['HIPHOP', 'POP'],
    'Fact': ['HIPHOP', 'POP'],
    'Grundulis': ['HIPHOP', 'POP'],
    'Mixeri': ['HIPHOP', 'POP'],
    'Cits Kvartāls': ['HIPHOP', 'POP'],
    'Bāze 7': ['HIPHOP', 'POP'],

    # ═══════════════════════════════════════════════════════════════════════
    # FOLK / ETHNO
    # ═══════════════════════════════════════════════════════════════════════
    'Iļģi': ['FOLK', 'POP'],
    'Vilki': ['FOLK', 'POP'],
    'Laimas Muzykanti': ['FOLK', 'POP'],
    'Auļi': ['FOLK', 'SMAGAIS ROKS'],
    'Tautumeitas': ['FOLK', 'POP'],
    'Dabasu Durovys': ['FOLK', 'POP'],
    'Zigfrīds Muktupāvels': ['FOLK', 'POP'],

    # ═══════════════════════════════════════════════════════════════════════
    # ELECTRONIC
    # ═══════════════════════════════════════════════════════════════════════
    'Singapūras Satīns': ['ELECTRO', 'POP'],
    'Zodiaks': ['POP', 'ELECTRO'],
    'Maija Lūsēna': ['POP', 'ELECTRO'],

    # ═══════════════════════════════════════════════════════════════════════
    # JAZZ
    # ═══════════════════════════════════════════════════════════════════════
    'Very Cool People': ['JAZZ', 'POP'],
}


def get_year(row):
    try: return int(row[COL_YEAR])
    except: return None

def get_era(row):
    try: return row[COL_ERA].strip().lower()
    except: return ''

def fuzzy_match_artist(artist_name, mapping):
    """Fuzzy match: longest case-insensitive substring match wins."""
    artist_lower = artist_name.lower().strip()
    matches = []
    for key in mapping:
        key_lower = key.lower().strip()
        if key_lower in artist_lower:
            matches.append((len(key_lower), key))
    if not matches:
        return []
    matches.sort(key=lambda x: -x[0])
    return list(mapping[matches[0][1]])

def compute_time_period(year, era):
    cats = set()
    if year is not None:
        if year <= 1987: cats.add('RETRO')
        elif 1988 <= year <= 1995: cats.add('ATMODA')
        elif year >= 2022: cats.add('JAUNUMI')
    else:
        if era == 'vintage': cats.add('RETRO')
        elif era == 'vcr': cats.add('ATMODA')
    return cats

def compute_style_genres(artist, song, year, era):
    genres = set()
    matched = fuzzy_match_artist(artist, artist_genres)
    genres.update(matched)

    artist_lower = artist.lower()

    # Special: Līvi vintage era = LĀGERIS (not modern POP)
    if 'līvi' in artist_lower:
        if year is not None and year <= 1987:
            genres.discard('POP')
            genres.add('LĀGERIS')
        # Līvi 1988+ keeps POP + LĀGERIS from mapping

    # Song name keywords
    song_lower = (song or '').lower()
    if any(kw in song_lower for kw in ['rock', 'metal', 'punk']):
        genres.add('SMAGAIS ROKS')
    if any(kw in song_lower for kw in ['disco', 'disko']):
        genres.add('DEJU MŪZIKA')

    # Remove time-period cats
    genres -= TIME_PERIOD_CATS

    # Default if nothing matched
    if not genres:
        if era == 'vintage' or (year is not None and year <= 1987):
            genres.update(['LĀGERIS', 'POP'])
        else:
            genres.add('POP')

    return genres

def ensure_two(genres, artist, song, year, era):
    """Ensure at least 2 categories total."""
    if len(genres) >= 2:
        return genres
    
    # Only 1 category
    cat = list(genres)[0] if genres else None
    
    if cat in TIME_PERIOD_CATS:
        # Only time-period, add default style
        if era == 'vintage' or (year and year <= 1987):
            genres.add('LĀGERIS')
        else:
            genres.add('POP')
    elif cat in STYLE_CATS:
        # Only style, no time-period (1996-2021)
        # Add POP as catchall secondary if not already POP
        if cat != 'POP':
            genres.add('POP')
        else:
            # POP only, from 1996-2021 with no artist match giving 2nd genre
            # This shouldn't happen now since all artists in mapping have 2 genres
            # But as fallback: add LĀGERIS for older, ELECTRO for newer
            if year and year < 2005:
                genres.add('LĀGERIS')
            else:
                genres.add('ELECTRO')
    else:
        genres.add('POP')
    
    return genres


def main():
    rows = []
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            rows.append(row)

    print(f"Read {len(rows)} songs from input file.")
    print()

    output_rows = []
    stats_per_cat = Counter()
    stats_cat_count = Counter()
    changes_made = 0
    unmatched_artists = Counter()

    for row in rows:
        while len(row) < 26:
            row.append('')

        artist = row[COL_ARTIST]
        song = row[COL_SONG]
        year = get_year(row)
        era = get_era(row)

        # Preserve manually-set rare categories
        existing_special = set()
        for i, gname in enumerate(GENRE_NAMES):
            if row[GENRE_START + i].strip().upper() == 'X' and gname in {'RZEMJU', 'LIVE', 'BĒRNU', 'DZIESMU ŠOV'}:
                existing_special.add(gname)

        # Compute fresh
        time_cats = compute_time_period(year, era)
        style_cats = compute_style_genres(artist, song, year, era)
        
        # Track unmatched artists
        matched = fuzzy_match_artist(artist, artist_genres)
        if not matched:
            unmatched_artists[artist] += 1

        final_genres = time_cats | style_cats | existing_special
        final_genres = ensure_two(final_genres, artist, song, year, era)

        # Track changes
        original_genres = set()
        for i, gname in enumerate(GENRE_NAMES):
            if row[GENRE_START + i].strip().upper() == 'X':
                original_genres.add(gname)
        if final_genres != original_genres:
            changes_made += 1

        # Write
        for i, gname in enumerate(GENRE_NAMES):
            row[GENRE_START + i] = 'X' if gname in final_genres else ''

        output_rows.append(row)
        for gname in final_genres:
            stats_per_cat[gname] += 1
        stats_cat_count[len(final_genres)] += 1

    # Write TSV
    with open(OUTPUT_FILE, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        for row in output_rows:
            writer.writerow(row)

    print(f"Output: {OUTPUT_FILE}")
    print(f"Modified: {changes_made} / {len(rows)}")
    print()

    print("=" * 60)
    print("SONGS PER CATEGORY:")
    print("=" * 60)
    for gname in GENRE_NAMES:
        c = stats_per_cat.get(gname, 0)
        bar = '#' * (c // 2)
        print(f"  {gname:20s}: {c:4d}  {bar}")
    total_marks = sum(stats_per_cat.values())
    print(f"\n  Total category marks: {total_marks} across {len(rows)} songs")
    print(f"  Average categories per song: {total_marks/len(rows):.2f}")
    print()

    print("=" * 60)
    print("CATEGORY COUNT DISTRIBUTION:")
    print("=" * 60)
    for k in sorted(stats_cat_count):
        print(f"  {k} categories: {stats_cat_count[k]:4d} songs")
    print()
    total = len(rows)
    w1 = stats_cat_count.get(1, 0)
    w2 = stats_cat_count.get(2, 0)
    w3 = sum(v for k, v in stats_cat_count.items() if k >= 3)
    w2p = sum(v for k, v in stats_cat_count.items() if k >= 2)
    print(f"  1 category:   {w1:4d} songs")
    print(f"  2 categories: {w2:4d} songs")
    print(f"  3+ categories: {w3:3d} songs")
    print(f"  >= 2 total:   {w2p:4d} / {total} ({100*w2p/total:.1f}%)")
    print()

    # Unmatched artists
    if unmatched_artists:
        print("=" * 60)
        print(f"UNMATCHED ARTISTS (defaulted by era): {sum(unmatched_artists.values())} songs")
        print("=" * 60)
        for a, c in unmatched_artists.most_common():
            print(f"  {a:50s} x{c}")
        print()

    # Songs with only 1 category
    if w1 > 0:
        print("=" * 60)
        print("SONGS WITH ONLY 1 CATEGORY:")
        print("=" * 60)
        for row in output_rows:
            gi = [GENRE_NAMES[i] for i in range(len(GENRE_NAMES)) if row[GENRE_START+i].strip()=='X']
            if len(gi) == 1:
                print(f"  {row[COL_ARTIST]:40s} | {row[COL_SONG]:30s} | {row[COL_YEAR]:5s} | {gi}")
    else:
        print("All songs have >= 2 categories!")
    print()

    # Sample output
    print("=" * 60)
    print("SAMPLE OUTPUT (first 15 + last 10):")
    print("=" * 60)
    for row in output_rows[:15]:
        gi = [GENRE_NAMES[j] for j in range(len(GENRE_NAMES)) if row[GENRE_START+j].strip()=='X']
        print(f"  {row[COL_ARTIST]:40s} | {row[COL_SONG]:25s} | {row[COL_YEAR]:5s} | {gi}")
    print("  ...")
    for row in output_rows[-10:]:
        gi = [GENRE_NAMES[j] for j in range(len(GENRE_NAMES)) if row[GENRE_START+j].strip()=='X']
        print(f"  {row[COL_ARTIST]:40s} | {row[COL_SONG]:25s} | {row[COL_YEAR]:5s} | {gi}")

if __name__ == '__main__':
    main()
