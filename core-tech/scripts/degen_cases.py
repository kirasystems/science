import sys

def parse_span_file(filename):
  spans = []
  with open(filename) as fil:
    for line in fil:
      start,end = map(lambda x: int(x),line.strip().split())
      spans.append({'start' : start, 'end':(end + 1)})
  return spans

def span_overlaps(A,B):
  return not ( (A['end'] <= B['start']) or  (A['start'] >= B['end']))

def span_contains(A,B):
  return ( (A['start'] >= B['start']) and (A['end'] <= B['end'])) 
 
def overlapping_spans(A,B):
  return [a for a in A if any(span_overlaps(a,b) for b in B)]

def non_overlapping_spans(A,B):
  return [a for a in A if not(any(span_overlaps(a,b) for b in B))]

def multiple_overlaps(A,B):
  return [a for a in A if len([b for b in B if span_overlaps(a,b)]) > 1]

def complete_overlaps(A,B):
  return [a for a in A if any(span_contains(a,b) for b in B)]

gold = parse_span_file(sys.argv[1])
pred = parse_span_file(sys.argv[2])
broken_annotations = multiple_overlaps(gold,pred)
incomplete_annotations = len(gold) - len(complete_overlaps(gold,pred)) - len(non_overlapping_spans(gold,pred))
total = len(gold)
#for i in complete_overlaps:
#  print i['start'],i['end']
print incomplete_annotations / float(total), len(broken_annotations)/float(total)

