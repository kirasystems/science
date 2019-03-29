# Variations in Assessor Agreement in Due Diligence
*Adam Roegiest and Anne McNulty*  
CHIIR 2019

## Data Collection
The annotated spans by human and machine annotators as well as text renderings of the documents are
being released as a part of the Kira Systems collection (for non-commercial use). To gain access to the collection (in whole or part), researchers are required to fill out and submit [this](https://kirasystems.com/files/Kira-Systems-Information-Release-Application.pdf) agreement to `science at kirasystems dot com`. Upon receipt and successful processing of the executed agreement, researchers will be provided access to a download system that will enable them to retrieve the test collection. Specific instructions will be provided in the follow-up email. 

Note that at the moment, we are not releasing featurized versions of the annotated documents. Accordingly, to replicate any of the machine learned models will require featurizing the documents and aligning the provided spans to those labels. 

## Preliminaries
To run these scripts, you require a recent installation of Go (i.e., 1.11) that supports modules and/or are willing to put this repo in your go path. Once this is setup, you need to simply 
run `pushd src && go build -o agree *.go && cp agree ../ && popd` to generate an executable that you can use  with the commands outlined below to conduct the same analyses as in the paper.

For simplicity, we will also assume the data for the study is located in `study-data`.

## Human Annotator Agreement

To replicate the results from Tables 2 and 3 of the paper, one simply needs the command: `./agree study-data/annotator-docs.txt study-data/annotator-results`.

This will output a 5 by 8 tab separate matrix of scores for Assesor Combination, Reecall, Precision, Cohen's Kappa, Overlap, Granular Recall, Granular Precision, and Granular Overlap.

The Assessor Combinations are specified in order of Primary (gold) assessor and the Seconday assessor being evaluated.

## Machine Annotator Agreement

We note that Table 4 was generated based upon our internal system training the models and so cannot given code to replicate that exact table. Though in conjunction with the existing training scripts (in the core-tech subdirectory of this repository), the provided documents and spans, one could train their own versions of these models. 

To replicate the results from Table 5 of the paper, one simply needs the command: `./agree study-data/machine-docs.txt study-data/machine-results "Change of Control" "Assignment"  "Exclusivity" "Indemnity"`. Note that the Go program allows you to specify individual topics to evaluated on after the first two arguments. Accordingly, we omit "Most Favoured Nation" as not model identified any instances.

This will output a 5 by 8 tab separate matrix of scores for Assesor Combination, Reecall, Precision, Cohen's Kappa, Overlap, Granular Recall, Granular Precision, and Granular Overlap.

The Assessor Combinations are specified in order of Primary (gold) assessor and the Seconday assessor being evaluated. Note that in this case this refers to the actual machine learned models' training user. 