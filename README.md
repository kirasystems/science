# Kira Science Repository

This repository contains links to source code and data agreements for replication of results formally published by the Kira Research team. Each paper is given its own subdirectory and README with any necessary context or information.

Please feel free to contact the authors or post an issue on this repository if you have questions or concerns.

## A Dataset and an Examination of Identifying Passages for Due Diligence
*Adam Roegiest, Alexander K. Hudek, and Anne McNulty*
SIGIR 2018

We present and formalize the due diligence problem, where lawyers extract data from legal documents to assess risk in a potential merger or acquisition, as an information retrieval task. Furthermore, we describe the creation and annotation of a document collection for the due diligence problem that will foster research in this area. This dataset comprises 50 topics over 4,412 documents and ~15 million sentences and is a subset of our own internal training data.

Using this dataset, we present what we have found to be the state of the art for information extraction in the due diligence problem. In particular, we find that when treating documents as sequences of labelled and unlabelled sentences, Conditional Random Fields significantly and substantially outperform other techniques for sequence-based (Hidden Markov Models) and non-sequence based machine learning (logistic regression). Included in this is an analysis of what we perceive to be the major failure cases when extraction is performed based upon sentence labels.

