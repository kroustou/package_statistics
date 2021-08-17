#!/usr/bin/env python3
import argparse
import sys
import gzip
import requests
import logging

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)


class ContentParser:
    """
    Parses a debian repository
    """

    def __init__(self, repository: str):
        # Clear tailing slash
        if repository[-1] == "/":
            repository = repository[:-1]
        self._repository = repository

    def _sort(self, packages: dict) -> dict:
        return dict(
            sorted(
                packages.items(),
                key=lambda x: x[1],
                reverse=True,
            )
        )

    def _get_contents(self, arch: str) -> bytes:
        """
        Gets the content file for given arch
        from the repository and returns its contents
        Raises exceptions in case the request or decompression fails
        """
        contents_path = f"{self._repository}/Contents-{arch}.gz"
        logging.debug("Getting %s", contents_path)
        contents_request = requests.get(contents_path)
        logging.debug(
            "Done getting %s, status %s",
            contents_path,
            contents_request.status_code,
        )
        contents_request.raise_for_status()
        return gzip.decompress(contents_request.content)

    def get_statistics(self, arch: str, count: int = 10) -> dict:
        """
        Gets the statistics for given arch. Returns a dictionary with
        the first n packages with the top # of files associated with them.
        Raises exceptions in case something goes wrong
        """
        # initialize dict
        top_packages = {}
        try:
            contents = self._get_contents(arch)
        except Exception as err:
            logging.error(err)
            raise
        # TODO iterate over a generator, since the content
        # could be quite long
        first_line, rest = contents.split(b"\n", 1)
        # check if the first line contains
        if not("FILE" in first_line.decode() or "LOCATION" in first_line.decode()):
            logging.warning("Missing FILE/LOCATION headers")
            rest = first_line + b"\n" + rest
        for package in rest.split(b"\n"):
            try:
                # split on the last space character
                name, associated_files = package.rsplit(b" ", 1)
            except ValueError:
                # in case this line cannot be split, continue
                continue
            name = name.strip()
            # get number of files
            number_of_associated_files = len(associated_files.split(b","))
            # if we have already gathered the top n packages so far...
            if len(top_packages.values()) == count:
                # let's sort the dict to get the one with the smallest
                # number of associated files
                top_packages = self._sort(top_packages)
                # get the ordered values
                values = top_packages.values()
                if list(values)[count - 1] < number_of_associated_files:
                    logging.debug("Insert %s", name)
                    # remove the last item
                    top_packages.popitem()
                    # add the next one
                    top_packages.update(
                        {name.decode("utf-8"): number_of_associated_files}
                    )
            else:
                top_packages.update(
                    {name.decode("utf-8"): number_of_associated_files}
                )
        return self._sort(top_packages)


def get_arch_stats(arch: str, repository: str) -> str:
    # initialize class
    content_parser = ContentParser(repository)
    try:
        top = content_parser.get_statistics(arch)
    except Exception as e:
        sys.exit(e)
    else:
        print(arch)
        print("---------")
        for i, (package, files) in enumerate(top.items(), 1):
            print(f"{i}. {package} {files}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get repository contents.")
    parser.add_argument(
        "arch",
        metavar="ARCH",
        type=str,
        nargs="+",
        help="positional: architectures (mips, amd64)",
    )
    parser.add_argument(
        "--repository",
        required=True,
        dest="repository",
        help="repository to use"
    )
    args = parser.parse_args()
    for a in args.arch:
        get_arch_stats(a.lower(), args.repository)
