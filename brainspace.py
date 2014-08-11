import math
import os
import hashlib
import random

hard_max_neurons_per_unit = 64
hard_max_axons_per_unit=128
hard_io_max=16
axon_weight_max=1

test_length=6
test_n=6

def logistic(x):
    r=1+math.pow(math.e,-1*x)
    d=math.pow(r,-1)
    return d

class neuron:

    def __init__(self, id):
        self.amount=0
        self.id=id
        self.downstream_axons=[]


class axon:
    def __init__(self, id, destination, weight):
        self.weight=weight
        self.id=id
        self.destination_neuron=destination

class unit:
    def __init__(self):
        self.neurons=[]
        self.axons=[]
        self.input_neurons=[]
        self.output_neurons=[]
        self.id=-1

        self.rawgenome=-1
        
    def clearall(self):
        self.neurons=[]
        self.axons=[]
        self.input_neurons=[]
        self.output_neurons=[]
        self.id=-1
        self.rawgenome=-1

    def generate(self, intgenome):
        #self.resetneurons()
        genome=int_to_genome(intgenome)
        self.clearall()
        self.rawgenome=intgenome

        for i in range(0,genome['neurons_n']):
            a=neuron(i)
            self.neurons.append(a)

        for i in range(0,genome['axons_n']):
            b=axon(i, genome['axons'][i]['dest'], genome['axons'][i]['weight'])
            self.axons.append(b)
            source=genome['axons'][i]['source']
            self.neurons[source].downstream_axons.append(i)

        for x in genome['inputs']:
            self.input_neurons.append(x)
        for y in genome['outputs']:
            self.output_neurons.append(y)

    def reset_neurons(self):
        for i in range(0,len(self.neurons)):
            self.neurons[i].amount=0

    def fire(self):
        for x in self.neurons:
            logisticx=logistic(x.amount)
            for a in x.downstream_axons:
                axonweight=self.axons[a].weight
                amounttosend=axonweight*logisticx
                destneuron=self.axons[a].destination_neuron
                self.neurons[destneuron].amount=self.neurons[destneuron].amount+amounttosend
            self.neurons[x.id].amount=0

    def outputs(self):
        results=[]
        for x in self.output_neurons:
            value=self.neurons[x].amount
            results.append(value)
        return results

    def set_inputs(self,data):
        if len(data)>=len(self.input_neurons):
            for i in range(0,len(self.input_neurons)):
                self.neurons[self.input_neurons[i]].amount=data[i]
        else:
            for i in range(0,len(data)):
                self.neurons[self.input_neurons[i]].amount=data[i]
            for i in range(len(data),len(self.input_neurons)):
                self.neurons[self.input_neurons[i]].amount=0

    def AND_test(self):
        global outs
        randominputs=[]
        for i in range(0,test_n):
            rand1=random.random()*2-1
            rand2=random.random()*2-1
            randominputs.append([rand1,rand2])
        #print randominputs

        mycode=self.rawgenome

        score=0
        
        for i in range(0,test_n):
            self.reset_neurons()
            
            #INITIALIZE BETWEEN TESTS
            self.set_inputs(randominputs[i])
            
            for d in range(0,test_length):
                self.fire()

            outs=self.outputs()
            if randominputs[i][0]>0 and randominputs[i][1]>0:
                if outs[0]>0:
                    score=score+100.0/(test_length*test_n)
            else:
                if outs[0]<0:
                    score=score+100.0/(test_length*test_n)

        print score
        return score
            
            

    

def int_to_genome(n):
    genome={}
    genome['neurons_n']= n%hard_max_neurons_per_unit + 1
    n=n/hard_max_neurons_per_unit

    genome['axons_n']=n%hard_max_axons_per_unit+1
    n=n/hard_max_axons_per_unit

    genome['axons']=[]
    for i in range(0,genome['axons_n']):
        axondata={}
        axondata['source']=int(n%genome['neurons_n'])
        n=n/genome['neurons_n']
        axondata['dest']=int(n%genome['neurons_n'])
        n=n/genome['neurons_n']
        axondata['weight']=(float(n%1000)/1000.0*2-1.0)*axon_weight_max
        n=n/1000
        genome['axons'].append(axondata)

    genome['inputs_n']=int((n%(genome['neurons_n']))+1)
    n=n/genome['neurons_n']
    genome['inputs']=[]
    for i in range(0,genome['inputs_n']):
        inpn=int(n%genome['neurons_n'])
        n=n/genome['neurons_n']
        genome['inputs'].append(inpn)    

    genome['outputs_n']=int((n%genome['neurons_n'])+1)
    n=n/genome['neurons_n']
    genome['outputs']=[]
    for i in range(0, genome['outputs_n']):
        outpn=int(n%genome['outputs_n'])
        n=n/genome['outputs_n']
        genome['outputs'].append(outpn)
    
   
    #print n
    return genome


def mutate_genome(rawgenome, fraction_mutated):  #fraction mutation is average
    global genomelist
    point_mutations_average=fraction_mutated*float(len(str(rawgenome)))
    #actual point mutations fluctuates around that average fraction

    pointmutations = (math.erf(float(random.randrange(-50,50))/100.0)+1)*point_mutations_average
    pointmutations=int(pointmutations)
    if pointmutations<0:
        pointmutations=0
    if pointmutations>len(str(rawgenome)):
        pointmutations=len(str(rawgenome))
    #print pointmutations
    alldone=False
    mutationcount=0

    genomelist=list(str(rawgenome))
    
    while not alldone:
        if mutationcount>=pointmutations:
            alldone=True
            
        else:
            randposition=random.randrange(0,int(len(str(rawgenome))-2))
            decider=random.random()
            if decider>=0.5:
                genomelist[randposition]=str(int(genomelist[randposition])+1)
                if genomelist[randposition]=='10':
                    genomelist[randposition]='0'
                mutationcount=mutationcount+1
            else:
                genomelist[randposition]=str(int(genomelist[randposition])-1)
                if genomelist[randposition]=='-1':
                    genomelist[randposition]='0'
                mutationcount=mutationcount+1

    
    rawgenome=''.join(genomelist)
    rawgenome=long(rawgenome)
    return rawgenome

def crossover_genomes(genomea, genomeb):  #CROSSOVER 50/50
    #THIS IS PROBLEMATIC BECAUSE CHILDREN WILL HAVE ALMOST NO TRAITS FROM PARENTS ACCORDING TO GENOME PARSING
    crossovertimes=(len(genomea)+len(genomeb))/
    
    
        
    

def randint():
    loglimit=6+7*hard_max_axons_per_unit
    return random.getrandbits(loglimit*5)

def random_genome():
    a=randint()
    print a
    genome=int_to_genome(a)
    return genome


class ecosystem:
    def __init__(self, units_n):
        self.units=[]
        for i in range(0,units_n):
            r=unit()
            r.generate(randint())
            self.units.append(r)


    def run_tests(self):
        scores=[]
        for i in range(0,len(self.units)): #NEED TO GENErALIZE TESTS
            scores.append(self.units[i].AND_test())
        return scores

    #def crossover_unit_pair(self, unit_a, unit_b):

    #def crossover_fraction(self, fraction):  #CROSSOVER FRACTION OF UNITS RANDOMLY

    #def cull(self, score_exponent_base): #exponential probability of survival based on score    
        #kills WEAK PROGRAMS

    def mutate_fraction(self, fraction_to_mutate, fraction_of_mutation):
        alldone=False
        total_to_mutate=int(fraction_to_mutate*len(self.units))
        total_already_mutated=0
        while not alldone:
            if total_already_mutated>=total_to_mutate:
                alldone=True
            else:
                randomchoice=random.randrange(0,len(self.units))
                oldgenome=self.units[randomchoice].rawgenome
                newgenome=mutate_genome(oldgenome, fraction_of_mutation)
                self.units[randomchoice].generate(newgenome)
                total_already_mutated=total_already_mutated+1
                print str(total_already_mutated)+" / "+str(total_to_mutate)
                

    

a=ecosystem(100)
a.mutate_fraction(0.1,0.02)





