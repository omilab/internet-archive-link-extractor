# Internet Archive Link Extractor
This tool was built to extract external links of a website snapshots in the Internet Archive. The output can be used to preform link analysis on website.

### Preparations

1. Download or clone the project.
2. Install requirements
```bash
pip install -r requirements.txt
```

### Usage

Create file with list of URLs, each URL in new line. Then run the command:
```bash
python link_extractor.py -i filename
```


To get help about the optional parameters run:
```bash
python link_extractor.py -h
```

### Output Format

The format of the output file is JSON. 
Each line in the output file represents one URL from the input file and all the external links that found in each snapshot.   

 