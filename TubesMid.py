import nltk

train = open('datatrain.txt','w')
sentences = open('sentences.txt').read().lower()
token = nltk.word_tokenize(sentences)
totalWord={}


def dataread(): #create the POSTagging list
    dict = {}
    tahap = 0
    dict['s.t.r'] ={}
    dict['s.t.r']['start'] = tahap
    with open('input_text.txt') as data:
        while tahap<=500:
            sent = data.readline()
            sent = sent.lower()
            if len(sent.strip()) == 0:
                continue
            if '#eot#' in sent or tahap == 101:
                break
            sentence = sent
            if ('#' in sent):
                tahap +=1
                continue
            sentence = sentence.split("\t")
            if (sentence[2]=="_"):
                tag = sentence[3]
            else:
                tag = sentence[2]
            if (sentence[1] in dict):
                if (tag in dict[sentence[1]]):
                    dict[sentence[1]][tag] +=1
                else:
                    dict[sentence[1]][tag] = 1
            else:
                dict[sentence[1]] ={}
                dict[sentence[1]][tag] = 1
        dict['s.t.r']['start'] = tahap
    return dict

def datawrite(train): #USE WHOLE SENTENCE as Data Train
    tahap = 0
    loop = True
    with open('input_text.txt') as data:
        while tahap <=500:
            sent = data.readline()
            sent = sent.lower()
            if len(sent.strip()) == 0:
                continue
            if tahap == 4477:
                break
                loop == False
            sentence = sent
            if ('# sent_id' in sent):
                print('write', tahap)
                sent = data.readline()
                sentence = sent.split("text = ")[1]
                print(sentence)
                train.write('s.t.r '+sentence.lower())
                tahap +=1


datawrite(train)
newfile = open('datatrain.txt').read()
newfile = newfile.replace("'"," ' ").replace('2012.','2012 .')
tokens = nltk.word_tokenize(newfile)

def count(word): #Count the amount of each occurrence words
    countword ={}
    num = 0
    for i in tokens:
        if (i == '``') or (i == "''"):
            i = '"'
        if i == word:
            if word in countword:
                countword[word] += 1
                num +=1
            else:
                countword[word] = 1
                num =+1
        else:
            pass
    return num


def emiProb(dict):
    prob = {}
    for k,v in dict.items():
        for k2, v2 in dict[k].items():
            if k not in prob:
                prob[k] ={}
                if k  == 's.t.r':
                    prob[k] = {}
                    prob[k]['start'] =1
                if (count(k) == 0):
                    #BONUS, smoothing is did in here
                    prob[k][k2] = 1
                else:
                    #print('kata',k,'tag',k2,dict[k][k2])
                    #print('huruf',k,'ada',count(k))
                    prob[k][k2] = dict[k][k2]/count(k)
            else:
                if k2 not in prob[k]:
                    prob[k][k2] = dict[k][k2]/count(k)
    return prob

def countTag(dict,tag): #Create a POSTagger based on highest emission probability table.
    tagCount = {}
    num = 0
    for word in tokens:
        if (word == '``') or (word == "''"):
            word = '"'
        if word not in dict:
            continue
        for a,b in dict[word].items():
            if a == tag:
                if a not in tagCount:
                    tagCount[a] =1
                    num +=1
                else:
                    tagCount[a] +=1
                    num +=1
            else:
                pass
    return num


def postagg(dict,emiTag): #Create a POSTagger based on highest emission probability table.
    for i, j in emiTag.items():
        if len(j) > 1:
            print('The Ambiguity words',i,'found words =',len(j))
    hiEmi = {}
    for k,v in dict.items():
        for k2, v2 in dict[k].items():
            if k not in hiEmi:
                hiEmi[k] ={}
                hiEmi[k][k2] = emiTag[k][k2]
            else:
                if len(emiTag[k]) >1:
                    hiEmi[k]={}
                    t = max(emiTag[k])
                    hiEmi[k][t] = emiTag[k][t]
    return hiEmi

def transition(dict): #Create a tag transition probability table (bigram model, only record one previous tag)
    bigramCount = {}
    temp = {}
    length = len(tokens)
    for i in range(length-1):
        word1 = tokens[i]
        word2 = tokens[i+1]
        if word1 == '``' or word1 == "''":
            word1 = '"'
        if word2 == '``' or word2 == "''":
            word2 = '"'
        if word1 == 'm.':
            word1 = 'm'
        if word2 == 'm.':
            word2 = 'm'
        if word1 == 'pepper':
            word1 = "pepper's"
        if word2 == 'pepper':
            word2 = 'pepper\'s'
        if word1 not in dict or word2 not in dict:
            continue
        if ('&') in word1 or ('&') in word2:
            continue
        if word1 in dict:
            for j,k in dict[word1].items():
                if j not in bigramCount:
                    for m,n in dict[word2].items():
                        bigramCount[j] = {}
                        temp[j] = {}
                        bigramCount[j][m] = 1
                        temp[j][m] =1
                else:
                    for m,n in dict[word2].items():
                        if m in bigramCount[j]:
                            temp[j][m] +=1
                            bigramCount[j][m] = temp[j][m]/(countTag(dict,j))
                        else:
                            bigramCount[j][m]=1
                            temp[j][m]=1

    return bigramCount


def viterbi(emi, tra, datatest):
    temp = 1
    result = 0
    vit ={}
    taglist = []
    test = nltk.word_tokenize(datatest)
    for i in range(len(test)):
        if test[i] in emi:
            for a,b in emi[test[i]].items():
                if b >1.0:
                    b =1.0
                tag = a
                taglist.append(a)
                vit[test[i]]={}
                vit[test[i]] = a
        elif test[i] not in emi: #Smoothing Unknown word into Noun tag
            vit[test[i]] ={}
            vit[test[i]]['noun']=1.0
            for c,d in vit[test[i]].items():
                tag = c
                taglist.append(c)

        if tag in tra:
            if tag == 'start':
                f = 1
            else:
                for x,y in tra[tag].items():
                    ptag = taglist[i-1]
                    f = tra[ptag][tag]

        temp = temp*f*b
        #print('tem',temp)
    result = temp
    result = result*100 # the result in Percent
    hasil = result
    return hasil,'%'


listTag = dataread()
print(listTag)
print('Tokens:',tokens)

d1 = 's.t.r desa saya terletak di kecamatan buahbatu' #DataTEST

transTab = transition(listTag)
emission_probability = emiProb(listTag)
highestProb = postagg(listTag,emission_probability)

vite = viterbi(highestProb,transTab,d1)

print('Probability of a word labeled with a tag (emission probability)\n',emission_probability,'\n')
print("The words with each its highest probability",highestProb)
print('TAG TRANSITION LIST',transTab)
print('Result of data Test',vite)