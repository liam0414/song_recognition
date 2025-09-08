import musicbrainzngs

musicbrainzngs.auth("liam0414", "83191830")

artist_id = "c5c2ea1c-4bde-4f4d-bd0b-47b200bf99d6"
result = musicbrainzngs.get_artist_by_id(artist_id)

artist = result["artist"]
print("name:\t\t%s" % artist["name"])
print("sort name:\t%s" % artist["sort-name"])