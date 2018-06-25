import sys

qid=1
for line in sys.stdin:
  if line == "\n":
    qid += 1
    continue
  line = line.strip().split()
  label = line[0]
  if label == "B":
    label = 2
  features = map(lambda x: x.split(':'),line[1:])
  features = sorted(features,key=lambda x:int(x[0]))
  print label,"qid:{}".format(qid),' '.join(map(lambda x: "{0}:{1}".format(int(x[0])+1,x[1]),features))
