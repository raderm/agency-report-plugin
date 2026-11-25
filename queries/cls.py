# Hardened channel classifier. Two helper columns are computed once in the
# inner query (sc_n: lower-case code, with a pasted ActBlue link reduced to its
# refcode; sc_t: channel token from the dictionary's channel field, else the
# second part of any PREFIX_CHANNEL_... code), then the CASE reads them.
def helpers(code, scc):
    C = f"COALESCE({code}, '')"
    N = f"(CASE WHEN {C} LIKE '%refcode=%' THEN SUBSTRING_INDEX(SUBSTRING_INDEX({C}, 'refcode=', -1), '&', 1) ELSE {C} END)"
    n = f"LOWER({N}) AS sc_n"
    t = (f"UPPER(COALESCE(NULLIF({scc}, ''), CASE WHEN {N} REGEXP '^[A-Za-z0-9]{{2,8}}_[^_]+' "
         f"THEN SUBSTRING_INDEX(SUBSTRING_INDEX({N}, '_', 2), '_', -1) END, '')) AS sc_t")
    return n + ", " + t

def cls(p, code):
    # p: column prefix ('' or 'x.'); code: the raw code column (for the blank test)
    L, T, ch = p + 'sc_n', p + 'sc_t', p + 'channel'
    def like(*pats):
        return '(' + ' OR '.join(f"{L} LIKE '{q}'" for q in pats) + ')'
    return (f"CASE WHEN {ch} = 'email' THEN 'Email' WHEN {ch} = 'sms' THEN 'Text (SMS)' WHEN {ch} = 'facebook_ad' THEN 'Meta ads' "
            f"WHEN {ch} = 'google_ad' THEN 'Google ads' WHEN COALESCE({code}, '') = '' THEN 'No source code' "
            f"WHEN {T} IN ('EM', 'EMAIL') THEN 'Email' "
            f"WHEN {T} IN ('BC', 'P2P', 'TEXT', 'SMS', 'MMS', 'TXT') OR {T} LIKE 'P2P-%' THEN 'Text (SMS)' "
            f"WHEN {T} = 'RTL' THEN 'Rented lists' WHEN {T} = 'ABTY' THEN 'ActBlue thank-you page' "
            f"WHEN {T} IN ('AD', 'ADS') OR {L} LIKE 'rtiads%' THEN 'Paid ads (coded)' "
            f"WHEN {T} IN ('WEB', 'SITE', 'WEBSITE') THEN 'Website' "
            f"WHEN {T} IN ('DM', 'MAIL') THEN 'Direct mail' "
            f"WHEN {T} IN ('SOC', 'SOCIAL') THEN 'Social media' "
            f"WHEN {like('website%', 'web!_%', 'web-%', 'site!_%', 'site-%', '%!_site!_%', '%!_site')} THEN 'Website' "
            f"WHEN {like('email%', 'em!_%', '%!_email%', '%-email%')} THEN 'Email' "
            f"WHEN {like('sms%', 'mms%', 'txt%', '%p2p%', '%!_txt%', '%-txt%', '%!_sms%', '%-sms%')} THEN 'Text (SMS)' "
            f"WHEN {like('social%', '%socialmedia%', '%social-media%', '%social!_media%', '%twitter%', 'facebook', 'facebook-%', 'facebook!_%', 'instagram%', 'bluesky%', 'tiktok%', 'linktree%')} THEN 'Social media' "
            f"WHEN {L} REGEXP '^dm[0-9]' OR {like('%directmail%', '%direct-mail%', '%direct!_mail%')} THEN 'Direct mail' "
            f"WHEN {like('%-website%', '%!_website%', '%homepage%', 'home-%', 'hero-%', 'menu-%', '%-menu%', '%sticky%', '%popup%', 'nav-%', '%-nav%', '%header%', '%footer%', '%banner%', '%-cta%')} THEN 'Website' "
            f"ELSE 'Other source code' END").replace("!_", "\\_")
