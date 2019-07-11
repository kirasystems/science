# Kira Science Repository

This repository contains links to source code and data agreements for replication of results formally published by the Kira Research team. Each paper is given its own subdirectory and README with any necessary context or information.

Please feel free to contact the authors or post an issue on this repository if you have questions or concerns.

## A Dataset and an Examination of Identifying Passages for Due Diligence
*Adam Roegiest, Alexander K. Hudek, and Anne McNulty*  
SIGIR 2018

Code [here](core-tech/README.md)

We present and formalize the due diligence problem, where lawyers extract data from legal documents to assess risk in a potential merger or acquisition, as an information retrieval task. Furthermore, we describe the creation and annotation of a document collection for the due diligence problem that will foster research in this area. This dataset comprises 50 topics over 4,412 documents and ~15 million sentences and is a subset of our own internal training data.

Using this dataset, we present what we have found to be the state of the art for information extraction in the due diligence problem. In particular, we find that when treating documents as sequences of labelled and unlabelled sentences, Conditional Random Fields significantly and substantially outperform other techniques for sequence-based (Hidden Markov Models) and non-sequence based machine learning (logistic regression). Included in this is an analysis of what we perceive to be the major failure cases when extraction is performed based upon sentence labels.

## Variations in Assessor Agreement in Due Diligence
*Adam Roegiest and Anne McNulty*  
CHIIR 2019

Code [here](variations/README.md)

In legal due diligence, lawyers identify a variety of topic instances in a company’s contracts that may pose risk during a transaction. In this paper, we present a study of 9 lawyers conducting a simulated review of 50 contracts for five topics. We find that lawyers agree on the general location of relevant material at a higher rate than in other assessor agreement studies, but they do not entirely agree on the extent of the relevant material. Additionally, we do not find strong differences between lawyers who have differing levels of due diligence expertise.

If we train machine learning models to identify these topics based on each user’s judgments, the resulting models exhibit similar levels of agreement between each other as to the lawyers that trained them. This indicates that these models are learning the types of behaviour exhibited by their trainers, even if they are doing so imperfectly.
Accordingly, we argue that additional work is necessary to improve the assessment process to ensure that all parties agree on identified material.

## On Interpretability and Feature Representations: An Analysis of the Sentiment Neuron
*Jonathan Donnelly and Adam Roegiest*  
ECIR 2019

Code [here](ECIR2019code/README.md)

We are concerned with investigating the apparent effective-ness of Radford et al.’s “Sentiment Neuron,” [9] which they claim encapsulates sufficient knowledge to accurately predict sentiment in reviews.In our analysis of the Sentiment Neuron, we find that the removal of theneuron only marginally affects a classifier’s ability to detect and label sentiment and may even improve performance. Moreover, the effectiveness of the Sentiment Neuron can be surpassed by simply using 100 randomneurons as features to the same classifier. Using adversarial examples, we show that the generated representation containing the Sentiment Neuron(i.e., the final hidden cell state in a LSTM) is particularly sensitive to the end of a processed sequence. Accordingly, we find that caution needs to be applied when interpreting neuron-based feature representations and potential flaws should be addressed for real-world applicability

## On Tradeoffs Between Document Signature Methods for A Legal Due Diligence Corpus
*Adam Roegiest and Edward Lee* 
SIGIR 2019

Code [here](SIGIR2019/README.md)

While document signatures are a well established tool in IR, they have primarily been investigated in the context of web documents. Legal due diligence documents, by their nature, have more similar structure and language than we may expect out of standard web collections. Moreover, many due diligence systems strive to facilitate real-time interactions and so time from document ingestion to availability should be minimal. Such constraints further limit the possible solution space when identifying near duplicate documents. We present an examination of the tradeoffs that document signature methods face in the due diligence domain. In particular, we quantify the trade-off between signature length, time to compute, number of hash collisions, and number of nearest neighbours for a 90,000 document due diligence corpus.