
def format(ob):
    if not ob.isna().any():
        
        print(f"{ob['id']} ------ {ob['data']}")
    else:
        print("no notes for now")

def format_all(all_df):
    if not all_df.empty:
        for _, row in all_df.iterrows():
            format(row)
    else:
        print("No notes for now")
