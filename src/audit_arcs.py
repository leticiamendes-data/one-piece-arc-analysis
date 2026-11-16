"""Step 2 - Data audit for OnePieceArcs.csv.

Goal: check data quality BEFORE analysing anything.
Run from the project root:  python3 src/audit_arcs.py
"""
import pandas as pd

RAW_PATH = "data-raw/OnePieceArcs.csv"

df = pd.read_csv(RAW_PATH)

# 1. Basic shape and completeness
print("Rows, columns:", df.shape)
print("Missing values:", int(df.isna().sum().sum()))
print("Duplicated arcs:", int(df["Arc"].duplicated().sum()))

# 2. Percent columns are stored as text ("0.9%"): convert to numbers
for col in ["Manga%", "Anime%"]:
    df[col + "_num"] = df[col].str.rstrip("%").astype(float)
    print(f"{col} adds up to {df[col + '_num'].sum():.1f}% (should be ~100)")

# 3. TotalMinutes is just episodes * 24, so it carries no new information
is_derived = (df["TotalMinutes(avg 24)"] == df["TotalEpisodes"] * 24).all()
print("TotalMinutes == TotalEpisodes * 24 for every row:", bool(is_derived))

# 4. Anime-only arcs (filler / adaptation extras) have 0 manga chapters
anime_only = df[df["TotalChapters"] == 0]
print(
    f"Anime-only arcs: {len(anime_only)} arcs, "
    f"{anime_only['TotalEpisodes'].sum()} of {df['TotalEpisodes'].sum()} episodes"
)

# 5. Do episode ranges follow each other without overlaps?
end_episode = df["Start onEpisode"] + df["TotalEpisodes"]
gap = (df["Start onEpisode"].shift(-1) - end_episode).dropna()
print("Rows where the next arc does not start right after this one:")
print(df.loc[gap[gap != 0].index, ["Arc", "Start onEpisode", "TotalEpisodes"]].assign(gap=gap[gap != 0]))

# 6. Where does the dataset stop? (it is a snapshot in time)
print("Last arc:", df.iloc[-1]["Arc"])
print("Last episode covered:", int(end_episode.iloc[-1] - 1))
