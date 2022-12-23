import json
import queue
import threading
import argparse

from spider import spider


class LinkExtraction:
    def __init__(self):
        self.q = queue.Queue()
        self.args = None

    def parse_arguments(self):
        """ Parse arguments from the command line """
        parser = argparse.ArgumentParser(description='Links extractor from Internet Archive snapshots.')
        parser.add_argument('-i', '--input', help='File name of seed list of URLs', required=True)
        parser.add_argument('-o', '--output', help='Seed list of URLs', default='output.txt')
        parser.add_argument('-l', '--extraction-level', help='Extraction Level', default=0, type=int)
        parser.add_argument('-c', '--collapse', help='Fetch results per year=4|month=6|day=8', default=4, type=int)
        parser.add_argument('-n', '--number-of-spiders', help='Number of spiders (more spiders more computer resources)', default=2, type=int)
        self.args = parser.parse_args()

    def worker(self):
        """ Worker function that handles the full cycle of crawling one URL """
        while not self.q.empty():
            url = self.q.get()
            try:
                obj = {}
                links = spider.Spider(self.args.extraction_level,
                                      self.args.collapse).crawl(url)
                obj[url] = links
                if self.args.output is not None:
                    with open(self.args.output, 'a') as output_file:
                        output_file.write('%s\n' % json.dumps(obj))
                else:
                    print(json.dumps(obj))

            except Exception as ex:
                pass

            self.q.task_done()

    def run(self):
        """  """
        self.parse_arguments()

        with open(self.args.input, 'r') as input_file:
            for url in input_file:
                url = url.strip()
                if len(url) > 0:
                    self.q.put(url)

        for i in range(self.args.number_of_spiders):
            t = threading.Thread(target=self.worker)
            t.daemon = True
            t.start()

        self.q.join()


if __name__ == "__main__":
    LinkExtraction().run()
