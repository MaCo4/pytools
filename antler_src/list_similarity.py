import glob
import json
from itertools import combinations
from pprint import pprint


def compare_lists(list1, list2):
    set1, set2 = set(list1), set(list2)
    intersection = set1 & set2
    intersection_len = len(intersection)
    union = len(set1) + len(set2) - intersection_len
    return {
        'jaccard': intersection_len / union,
        'intersection': intersection,
        'intersection_len': intersection_len,
        'union': union
    }


def compare_all_lists(lists):
    result = []

    for list1, list2 in combinations(lists, 2):
        similarity = compare_lists(list1['tracks'], list2['tracks'])
        if similarity['intersection_len'] > 0:
            result.append((list1['name'], list2['name'], similarity))

    result.sort(key=lambda x: x[2]['jaccard'], reverse=True)  # Sort by Jaccard index, highest first
    return result


if __name__ == "__main__":
    backup_file = sorted(glob.glob("spotify_backup_*.json"), reverse=True)[0]
    with open(backup_file) as file:
        print("Importing list data from file {}...".format(backup_file))
        list_data = json.load(file)
        print("Comparing lists by Jaccard index...")
        list_similarities = compare_all_lists(list_data)
        for list_pair in list_similarities:
            similarity = list_pair[2]
            print("'{}' and '{}' is similar with {} tracks in common (Jaccard index: {})"
                  .format(list_pair[0], list_pair[1], similarity['intersection_len'], similarity['jaccard']))
