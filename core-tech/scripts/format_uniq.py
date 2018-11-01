import sys

tp=0
fp=0
fn=0
for line in sys.stdin:
  count,gold,pred = line.strip().split()
  gold = int(gold)
  pred = int(float(pred))
  if (gold != 1 and gold == pred):
    continue
  elif (gold != 1):
    fp = int(count)
  elif (pred != 1):
    fn = int(count)
  else:
    tp = int(count)
eps=0.000001
recall =  (tp / float(tp + fn + eps))
precision = (tp / float(tp + fp + eps))
f1 = 2 * (precision * recall) / (precision + recall + eps)
print tp, fp, fn, recall, precision, f1
