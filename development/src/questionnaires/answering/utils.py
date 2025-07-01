# -----------------------------------------------------------------------------------------------------------------

def in_records(targets : list[str], records : list[str]) -> bool:
    '''
    Verifies the presence of some aspects within the applicant's records
    '''
    for target in targets:
        if target in records:
            return True
    return False

# -----------------------------------------------------------------------------------------------------------------

def in_posts(targets : list[str], posts : list[str]) -> bool:
    '''
    Verifies the presence of some aspects within the applicant's posts
    '''
    for post in posts:
        for target in targets:
            if target in post:
                return True
    return False

# -----------------------------------------------------------------------------------------------------------------