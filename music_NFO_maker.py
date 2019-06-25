#!/home/pancrace/anaconda3/bin/python3
# coding: utf-8
"""Script de génération de NFO sur données musicales."""

from os import listdir
from os.path import basename, realpath, isdir
import re
import pymediainfo
import humanfriendly
import sys


def list_album_tracks(album):
    """Renvoie la liste des fichiers mp3 ou flac dans l'album."""
    return sorted([f for f in listdir(album) if re.search('.(mp3|flac)$', f)])


def getMeta(track):
    """Lit les metadonnées utiles pour la génération du fichier."""
    mediainfo = pymediainfo.MediaInfo.parse(track)
    meta = mediainfo.tracks[0].to_data()
    meta_audio = mediainfo.tracks[1].to_data()

    infos = {}
    infos["titre"] = meta["title"]
    infos["position"] = int(meta["track_name_position"])
    infos["duree_sec"] = meta["duration"] // 1000

    infos["artiste"] = meta["performer"]
    infos["album"] = meta["album"]
    try:
        infos["annee"] = meta["recorded_date"]
    except KeyError:
        infos["annee"] = "????"

    infos["codec"] = meta["file_extension"].upper()
    infos["bitrate"] = meta_audio["bit_rate"]
    infos["canaux"] = meta_audio["channel_s"]
    infos["frequence"] = meta_audio["sampling_rate"]
    infos["taille_oct"] = meta["file_size"]

    return infos


def process_album(album):
    """Genere une string d'informations générale liées à l'album et la liste des pistes."""
    tracks = list_album_tracks(album)
    if len(tracks) == 0:
        print("No tracks found for %s" % album)
        return ""

    print("Processing album %s..." % current_dir)

    try:
        track_infos = sorted([getMeta(album + "/" + track) for track in tracks],
                             key=lambda x: int(x["position"]))
    except Exception as e:
        print("ERREUR : Erreur dans la récupération des données pour l'album %s" % album)
        print(e)
        return ""

    totaltime_s = sum([item["duree_sec"] for item in track_infos])
    totalsize = sum([item["taille_oct"] for item in track_infos])

    out = "----------------------------------------------------------------------------\n"
    out += "============================== Artiste - Album =============================\n"
    out += "----------------------------------------------------------------------------\n\n"
    out += "Artiste\t\t\t : %s\n" % track_infos[0]["artiste"]
    out += "Album\t\t\t : %s\n" % track_infos[0]["album"]
    out += "Année\t\t\t : %s\n\n" % track_infos[0]["annee"]

    out += "Source\t\t\t : %s\n" % "CD"
    out += "Codec\t\t\t : %s\n" % track_infos[0]["codec"]
    out += "Bitrate\t\t\t : %s Kbps\n" % (track_infos[0]["bitrate"] // 1000)
    out += "Canaux\t\t\t : %s\n" % track_infos[0]["canaux"]
    out += "Fréquence\t\t : %s Hz\n\n" % track_infos[0]["frequence"]

    out += "Nombre de pistes\t : %s\n" % len(track_infos)
    out += "Temps de lecture total\t : %s min %s sec\n" % (totaltime_s // 60, totaltime_s % 60)
    out += "Taille totale\t\t : %s\n\n" % humanfriendly.format_size(totalsize)

    out += "----------------------------------------------------------------------\n"
    out += "============================ Liste Pistes ============================\n"
    out += "----------------------------------------------------------------------\n\n"

    for info in track_infos:
        print("---%s" % info["titre"])
        out += "%3d : %-50s \t[%d:%02d]\n" % (info["position"], info["titre"],
                                              info["duree_sec"] // 60,
                                              info["duree_sec"] % 60)

    out += "\n============================================================================\n"

    return out


if __name__ == "__main__":

    assert len(sys.argv) >= 3
    assert sys.argv[1].lower() in ["album", "discographie", "discography"]

    for current_dir in sys.argv[2:]:
        assert isdir(current_dir)

        if sys.argv[1].lower() == "album":
            # traite un seul dossier contenant les tracks
            file_content = process_album(current_dir)
        else:
            print("=== Discographie %s ===" % current_dir)
            # traite tous les dossier du repertoire mais ne génère qu'un fichier
            albumslist = sorted([pth for pth in listdir(current_dir)
                                 if isdir("%s/%s" % (current_dir, pth))])
            file_content = "".join([process_album("%s/%s" % (current_dir, album))
                                    for album in albumslist])

        filename = basename(realpath(current_dir))
        with open("%s.nfo" % filename, 'w') as fic:
            fic.write(file_content)
            # fic.close()
