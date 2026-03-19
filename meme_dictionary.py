"""
Meme Dictionary Module
======================
Maintains a built-in dictionary of internet slang and meme terminology.
For unknown terms, queries Urban Dictionary's public API.
"""

import logging

import requests

logger = logging.getLogger(__name__)

# Built-in meme/slang dictionary with current internet meanings (2025-2026)
BUILTIN_DICTIONARY: dict[str, str] = {
    "aura": (
        "An invisible energy or vibe someone gives off. Having 'aura' means you exude "
        "effortless coolness or confidence. 'Lost aura' = did something embarrassing."
    ),
    "sigma": (
        "A self-reliant, lone-wolf personality type. Originally from the 'sigma male grindset' "
        "meme. Now used both seriously and ironically to describe someone who doesn't follow "
        "social norms and walks their own path."
    ),
    "rizz": (
        "Short for 'charisma.' Refers to someone's ability to charm or flirt with others. "
        "'W rizz' = good game, 'L rizz' = failed attempt. Can be used as a verb: 'rizzed up.'"
    ),
    "rizzed": (
        "Past tense of 'rizz.' Means someone successfully charmed or attracted another person. "
        "'She got rizzed' = she was won over by someone's charisma."
    ),
    "skibidi": (
        "Originates from 'Skibidi Toilet,' a YouTube animated series featuring heads in toilets. "
        "Now used as a general brainrot exclamation or adjective meaning chaotic, nonsensical, "
        "or absurd. Core element of 2024-2026 internet brainrot culture."
    ),
    "brainrot": (
        "The state of being so consumed by internet culture and memes that your vocabulary "
        "and thought patterns are permanently altered. Also describes content that causes this state. "
        "Example: 'My brainrot is terminal — I just said skibidi out loud in class.'"
    ),
    "gyatt": (
        "An exclamation of surprise or admiration, typically about someone's appearance. "
        "Derived from 'god damn.' Popularized by Twitch streamer YourRAGE."
    ),
    "slay": (
        "To do something exceptionally well or to look amazing. 'She absolutely slayed that outfit.' "
        "Originally from drag/ballroom culture, now mainstream internet slang."
    ),
    "ratio": (
        "When a reply gets more likes than the original post, indicating the original take was bad. "
        "'Ratio + L + you fell off' is a common roast combo."
    ),
    "npc": (
        "Non-Player Character. Used to describe someone who acts like they're running on a script — "
        "no original thoughts, just following trends. Also refers to TikTok NPC livestream trend."
    ),
    "delulu": (
        "Short for 'delusional.' Someone who has unrealistic expectations or beliefs, especially "
        "about relationships or their own abilities. 'Delulu is the solulu' = being delusional "
        "is sometimes the solution."
    ),
    "sus": (
        "Suspicious or shady. Popularized by Among Us. 'That's kinda sus bro.'"
    ),
    "cap": (
        "A lie or to lie. 'No cap' = no lie / for real. 'That's cap' = that's a lie."
    ),
    "bet": (
        "An affirmative response meaning 'okay,' 'sure,' or 'sounds good.' "
        "'Wanna grab food?' 'Bet.'"
    ),
    "fire": (
        "Something that is extremely good, cool, or impressive. 'This beat is fire 🔥.'"
    ),
    "goat": (
        "Greatest Of All Time. Used to praise someone as the best in their field. "
        "'LeBron is the GOAT' (debatable)."
    ),
    "vibe": (
        "A feeling, mood, or atmosphere. 'Vibe check' = assessing someone's energy. "
        "Can be a verb: 'we're vibing.'"
    ),
    "stan": (
        "An extremely dedicated fan. From Eminem's song 'Stan.' Can be a verb: 'I stan BTS.' "
        "Not always negative — often used positively in fan culture."
    ),
    "based": (
        "Having opinions or doing things without caring about others' judgment. "
        "Being authentic and unapologetically yourself. Opposite of 'cringe.'"
    ),
    "cringe": (
        "Something embarrassing, awkward, or try-hard. The opposite of 'based.' "
        "'That TikTok was maximum cringe.'"
    ),
    "cope": (
        "A coping mechanism or rationalization. 'That's pure cope' = you're just telling "
        "yourself that to feel better. Often paired with 'seethe.'"
    ),
    "mewing": (
        "A jawline exercise involving pressing your tongue to the roof of your mouth. "
        "Became a meme where people dramatically pose while 'mewing' for the camera. "
        "Associated with looksmaxxing culture."
    ),
    "mogged": (
        "Being outshone or dominated by someone else, especially in looks. "
        "'He just mogged everyone in the room.' From looksmaxxing community."
    ),
    "bussin": (
        "Something that is really good, especially food. 'This pizza is bussin fr fr.' "
        "Sometimes shortened to 'buss.'"
    ),
    "fanum tax": (
        "When someone takes a portion of your food without asking. Named after Twitch streamer "
        "Fanum who would take bites of his friends' food. 'He just fanum taxed my fries.'"
    ),
    "hawk tuah": (
        "A viral phrase from a street interview that became a massive meme in 2024. "
        "The interviewee's enthusiastic delivery made it iconic internet content."
    ),
    "ohio": (
        "In meme culture, Ohio is portrayed as a cursed, chaotic wasteland where the craziest "
        "things happen. 'Only in Ohio' = this is absolutely unhinged behavior."
    ),
    "simp": (
        "Someone who does way too much for a person they like, usually without reciprocation. "
        "'He donated $500 to her stream — down bad, total simp.'"
    ),
    "chad": (
        "A confident, attractive, successful male archetype. Used in memes as the ideal "
        "masculine figure. 'Chad move' = a bold, admirable action."
    ),
    "w": (
        "Short for 'Win.' A positive outcome. 'W take' = good opinion. Opposite of 'L.'"
    ),
    "l": (
        "Short for 'Loss.' A negative outcome or bad take. 'L + ratio + you fell off.'"
    ),
}


def _lookup_urban_dictionary(term: str) -> str | None:
    """
    Look up a term on Urban Dictionary's public API.
    Returns the top definition or None if not found.
    """
    url = "https://api.urbandictionary.com/v0/define"
    params = {"term": term}

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()

        data = resp.json()
        definitions = data.get("list", [])

        if definitions:
            # Get the top-voted definition
            top_def = sorted(definitions, key=lambda d: d.get("thumbs_up", 0), reverse=True)[0]
            definition = top_def.get("definition", "").replace("[", "").replace("]", "")
            # Truncate if too long
            if len(definition) > 300:
                definition = definition[:297] + "..."
            return definition

        return None

    except Exception as e:
        logger.warning(f"Urban Dictionary lookup failed for '{term}': {e}")
        return None


def lookup_terms(terms: list[str]) -> dict[str, dict]:
    """
    Look up a list of slang terms. Uses the built-in dictionary first,
    then falls back to Urban Dictionary for unknown terms.

    Returns a dict mapping term -> {definition, source}.
    """
    logger.info(f"📖 Looking up {len(terms)} slang terms in Meme Dictionary...")

    results = {}

    for term in terms:
        term_lower = term.lower().strip()

        # Check built-in dictionary first
        if term_lower in BUILTIN_DICTIONARY:
            results[term_lower] = {
                "definition": BUILTIN_DICTIONARY[term_lower],
                "source": "builtin_dictionary",
            }
            logger.info(f"  📗 '{term_lower}' → found in built-in dictionary")
        else:
            # Try Urban Dictionary
            logger.info(f"  🔍 '{term_lower}' → not in built-in dict, checking Urban Dictionary...")
            ud_def = _lookup_urban_dictionary(term_lower)
            if ud_def:
                results[term_lower] = {
                    "definition": ud_def,
                    "source": "urban_dictionary",
                }
                logger.info(f"  📕 '{term_lower}' → found on Urban Dictionary")
            else:
                results[term_lower] = {
                    "definition": "No definition found. This term may be too new or niche.",
                    "source": "not_found",
                }
                logger.info(f"  ❓ '{term_lower}' → no definition found")

    return results


def get_full_meme_dictionary() -> dict[str, dict]:
    """
    Returns the complete built-in meme dictionary with all known terms.
    """
    return {
        term: {"definition": defn, "source": "builtin_dictionary"}
        for term, defn in BUILTIN_DICTIONARY.items()
    }


if __name__ == "__main__":
    import json
    logging.basicConfig(level=logging.INFO)

    # Demo: look up a mix of known and unknown terms
    test_terms = ["sigma", "rizz", "aura", "skibidi", "glaze", "yapping"]
    results = lookup_terms(test_terms)
    print(json.dumps(results, indent=2))
