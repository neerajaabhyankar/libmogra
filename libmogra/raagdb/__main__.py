from libmogra.raagdb import PICKLE_PATH, write_pickle


raag_db = write_pickle()
print(f"wrote {len(raag_db)} raags to {PICKLE_PATH}")
