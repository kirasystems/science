import sys

def parse_span_file(filename):
  spans = []
  with open(filename) as fil:
    for line in fil:
      start,end = map(lambda x: int(x),line.strip().split())
      spans.append({'start' : start, 'end':(1 + end)})
  return spans

def span_overlaps(A,B):
  return not ( (A['end'] <= B['start']) or  (A['start'] >= B['end']))
 
def overlapping_spans(A,B):
  return [a for a in A if any(span_overlaps(a,b) for b in B)]

def non_overlapping_spans(A,B):
  return [a for a in A if not(any(span_overlaps(a,b) for b in B))]

gold = parse_span_file(sys.argv[1])
pred = parse_span_file(sys.argv[2])
eps = 0.000001
tp = len(overlapping_spans(gold,pred))
fp = len(non_overlapping_spans(pred,gold))
fn = len(non_overlapping_spans(gold,pred))
recall =  (tp / float(tp + fn + eps))
precision = (tp / float(tp + fp + eps))
f1 = 2 * (precision * recall) / (precision + recall + eps)
print tp, fp, fn, recall, precision, f1
