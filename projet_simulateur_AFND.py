from tkinter import *
from tkinter import messagebox, ttk, simpledialog
from copy import copy
import ast

# donnees par defaut a afficher dans la table de transition
global automate, down_frame, window_ruban, table_frame, deterministe, save_btn, saved_automate_frame

saved_automate_frame = None
window_ruban = None
down_frame = None
frame = None
table_frame = None

deterministe = True
etats_set = set()
alpha_set = set()
transit_dict = {}
initial = set()
accept_set = set()
automate = (etats_set,alpha_set,transit_dict,initial,accept_set)

dict_automate = {}

def lireMot(aut,mot):
    (etats,alpha,transit,init_set,accept)=aut
    lecture=[next(iter(init_set))]
    suivant=next(iter(init_set))
    for i in mot:
        if (suivant,i) in transit:
            suivant=next(iter(transit[(suivant,i)]))
            lecture.append({suivant})
        else:
            lecture.append(0)
            return (False,lecture)
    return (suivant in accept,lecture)

def lireND(aut,mot):
    (etats,alpha,T,init_set,accept)=aut

    L=[init_set] # Une liste d'ensembles
    etat=list(init_set)
    for c in mot:
        etat2=set()
        for e in etat:
            if (e,c) in T:
                etat2=etat2.union(T[(e,c)])
        if etat2:
            L.append(etat2)
        else : 
            L.append(0)
        etat=list(etat2)
        if etat==[]:
            return(False,L)
    return (etat2.intersection(accept)!={},L)

def lireNDe(aut,m):
    (etats,al,T,init,Ac)=aut
    Cl={i:cloture(aut,i) for i in etats} #On calcule une bonne fois toute les clôtures
    L=[init] # Une liste d'ensembles
    et=list(init)
    for c in m: # On calcule l'ensemble des états accessibles par lecture de la lettre c à partir d'un des états actuels
        et2=set()
        for i in et:
            for e in Cl[i]: #On calcule les transitions étendues à toute la clôture
                if (e,c )in T:
                    et2=et2.union(T[(e,c)])
        L.append(et2)
        et=list(et2)
        if et==[]:
            return(False,L)

    Ac2=set(Ac) #On n'oublie pas de faire hériter le caractère acceptant aux états possédant un état acceptant dans leur clôture
    for e in etats:
        if Cl[e].intersection(Ac)!={} and not e in Ac2:
            Ac2.add(e)
    return (et2.intersection(Ac2)!={},L)

# Fonction qui prend un automate et un etat sous forme d'entier, et renvoi la cloture de l'etat i dans l'automate
def cloture(aut,i):
    (etats,al,T,init,Ac)=aut

    Cl={i} # La clôture de l'état i
    L=[i]
    while L:
        j=L.pop(0)
        if (j,'€') in T:
            for k in T[(j,'€')]:
                if not k in Cl:
                    Cl.add(k)
                    L.append(k)
    return (Cl)

def determinise():
    global automate, table, table_frame, deterministe

    (etats,alpha,T,init,accept)=automate

    Cl={i:cloture(automate,i) for i in etats} #On calcule une bonne fois toute les clôtures
    Ac=set(accept) #On fait hériter le caractère acceptant aux états possédant un état acceptant dans leur clôture
    for e in etats:
        if Cl[e].intersection(accept)!=set() and not e in Ac:
            Ac.add(e)
            
    etatsD={1}
    k=1
    TD = {}
    initD={1}
    acceptD=set()
    L=[init] # La liste des états qu'il reste à traiter
    LM=[init]# La liste des états de l'AFD mémorisés 
    while L:
        et=L.pop(0)
        for c in alpha:
            et2=set()
            for i in et:
                if i in Cl:
                    for e in Cl[i]: #On calcule les transitions étendues à toute la clôture
                        if (e,c) in T:
                            et2=et2.union(T[(e,c)])
                else :
                    messagebox.showerror("Erreur", "L'automate ne comprend pas d'état " + str(i))
                    return

            if et2!=set():
                if  (et2 not in LM):
                    k+=1
                    etatsD.add(k)
                    LM.append(et2) 
                    L.append(et2)
                i=LM.index(et)+1
                j=LM.index(et2)+1
                TD[(i,c)]=j
                if et2.intersection(Ac)!=set():
                        acceptD.add(j)

    etats_var.set(str(max(etatsD)))
    transit_var.set(str(TD))
    init_var.set(str(initD))
    accept_var.set(str(acceptD))
    automate = (etatsD,alpha,TD,initD,acceptD)
    deterministe = True

    if table_frame and table_frame.winfo_exists():
        table_frame.destroy()
    table_frame = Toplevel(fenetre)
    table_frame.title("Table de transition")
    table = Table(table_frame)
        
def complet():
    global automate, table, table_frame

    (etats_set,alpha_set,transit_dict,initial,accept_set) = automate
    
    # Met à jour le texte de chaque widget Entry
    for (etat,letter) in table.entry:
        if table.entry[(etat,letter)].get()!="":
            temp = table.entry[(etat,letter)].get().replace('{','').replace('}','').split(',')
            transit_dict[(etat,letter)] = set([int(i) for i in temp])
    
    complet = (len(etats_set) * len(alpha_set)) == len(transit_dict)
    
    if not complet:
        puit = max(etats_set)+1
        etats_set.add(puit)
        for i in etats_set:
            for j in alpha_set:
                if (i,j) not in transit_dict:
                    transit_dict[(i,j)]=puit
    else :
        messagebox.showinfo("Information", "L'automate est déja complet")
        return
    # mise à jour de la valeur du champ "table de transition" dans la fenetre principale
    etats_var.set(str(max(etats_set)))
    transit_var.set(str(transit_dict))
    automate = (etats_set, alpha_set, transit_dict, initial, accept_set)

    if table_frame and table_frame.winfo_exists():
        table_frame.destroy()
    table_frame = Toplevel(fenetre)
    table_frame.title("Table de transition")
    table = Table(table_frame)

def emonder():
    global automate, table, table_frame

    (etats,alpha,T,init,Ac)=automate
    A=accessible(automate)
    B=coAccessible(automate)
    C=A.intersection(B) # Les sommets accessibles et co-accessibles
    L=list(C)
    #Les nouveaux états
    etats2={i+1 for i in range(len(C))}
    # La bijection entre états
    bij={L[i]:i+1 for i in range(len(C))}
    #Construction du nouvel automate
    Ac2={bij[i] for i in Ac}
    
    T2={}
    for (i,c) in T:
        j=next(iter(T[i,c]))
        if i in C and j in C:
            T2[(bij[i],c)]={bij[j]}
                
    etats_var.set(str(max(etats2)))
    transit_var.set(str(T2))
    init_var.set(str(bij[next(iter(init))]))
    accept_var.set(str(Ac2)[slice(1,len(str(Ac2))-1)])
    automate = (etats2,alpha,T2,{bij[next(iter(init))]},Ac2 )

    if table_frame and table_frame.winfo_exists():
        table_frame.destroy()
    table_frame = Toplevel(fenetre)
    table_frame.title("Table de transition")
    table = Table(table_frame)
    emond.grid_remove()

def coAccessible(aut):
    (etats,alpha,T,init,Ac)=aut
    #On construit le graphe inverse
    G={i:[] for i in etats}
    for i in etats:
        for c in alpha:
            if (i,c) in T:
                j=next(iter(T[(i,c)]))
                G[j].append(i)
                    
    coAccess={i for i in Ac}
    for e in Ac:
        L=[e]
        while L:
            i=L.pop(0)
            for j in G[i]:
                if not j in coAccess:
                    coAccess.add(j)
                    L.append(j)
    return coAccess
            
def accessible(aut):
    (etats,alpha,T,init,Ac)=aut
    Access=init # joue le rôle de visite
    L=[next(iter(init))]
    while L:
        i=L.pop(0)
        for c in alpha:
            if (i,c) in T:
                j=next(iter(T[(i,c)]))
                if not j in Access:
                    Access.add(j)
                    L.append(j)
    return Access            

def somme(A,B): # Effectue la somme de deux automates déterministes A et B. Le résultat sera un Automate fini NON déterministe.
    (etats1,al1,T1,init1,Ac1)=A
    (etats2,al2,T2,init2,Ac2)=B
    if al1!=al2:
        print("Les deux alphabets doivent être définis sur le même automate")
        return None
    else:
        p=len(etats1)
        n=p+len(etats2)
        etats={i+1 for i in range(n)}
        init={next(iter(init1)),p+next(iter(init2))}
        Ac=Ac1.union({p+i for i in Ac2})
        T=dict()
        for (i,c) in T1:
            T[(i,c)]={next(iter(T1[(i,c)]))}
        for (i,c) in T2:
            T[(p+i,c)]={p+next(iter(T2[(i,c)]))}
    return (etats,al1,T,init,Ac)

def produit(A,B): # Effectue le produit de deux automates déterministes A et B. Le résultat sera un Automate fini NON déterministe à € transitions.
    (etats1,al1,T1,init1,Ac1)=A
    (etats2,al2,T2,init2,Ac2)=B
    if al1!=al2:
        print("Les deux alphabets doivent être définis sur le même automate")
        return None
    else:
        #On fait l'union disjointe des deux automates
        p=len(etats1)
        n=p+len(etats2)
        etats={i+1 for i in range(n)}
        init={next(iter(init1))}        # Seul les états initiaux de A restent initiaux
        Ac= {i +p for i in Ac2}        # Seul les états acceptants de B restent acceptants
        al=copy(al1)
        al.add('€') 
        T=dict()
        for (i,c) in T1:
            T[(i,c)]={next(iter(T1[(i,c)]))}
        for (i,c) in T2:
            T[(p+i,c)]={p+next(iter(T2[(i,c)]))}
        # On ajoute les € transitions
        for i in Ac1:
            T[(i,'€')]={p+next(iter(init2))}
    return (etats,al,T,init,Ac)
        
def plus(A): # Calcule l'automate plus de l'automate déterministe A. Le résultat est un Automate fini NON déterministe à € transitions.
    (etats1,al1,T1,init1,Ac1)=A

    # On autorise les € transitions
    al=copy(al1)
    al.add('€')
    
    # On non déterminise la table de transition
    T=dict()
    for (i,c) in T1:
        T[(i,c)]={next(iter(T1[(i,c)]))}
    # On ajoute les € transitions
    for i in Ac1:
        T[(i,'€')]={next(iter(init1))}
    return (etats1,al,T,init1,Ac1)

def etoile(A): # Calcule l'étoile de l'automate déterministe A. Le résultat sera un Automate fini NON déterministe à € transitions.
    (etats1,al1,T1,init1,Ac1)=A
    n=len(etats1)
    # On autorise les € transitions
    al=copy(al1)
    al.add('€')
    # On ajoute un nouvel état initial acceptant
    etats=set(etats1)
    etats.add(n+1) 
    init={next(iter(init1)),n+1}
    Ac=set(Ac1)
    Ac.add(n+1)
    # On non déterminise la table de transition
    T=dict()
    for (i,c) in T1:
        T[(i,c)]={next(iter(T1[(i,c)]))}
    # On ajoute les € transitions
    for i in Ac1:
        T[(i,'€')]={next(iter(init1))}
    return (etats,al,T,init,Ac)

def inter(A,B): # Effectuant l'intersection de deux automates déterministes A et B en calculant l'automate des couples entre A et B. Le résultat sera un automate déterministe.
    (etats1,al1,T1,init1,Ac1)=A
    (etats2,al2,T2,init2,Ac2)=B
    if al1!=al2:
        print("Les deux alphabets doivent être définis sur le même automate")
        return None
    else:
        k=1
        etats={1}
        init=1
        bij={(next(iter(init1)),next(iter(init2))):1} # dictionnaire : bijection entre couples d'états et état de l'automate produit 
        Ac=set()
        T=dict()
        L=[(next(iter(init1)),next(iter(init2)))]# liste des états restant à traiter
        while L:
            (i,j)=L.pop(0)
            I=bij[(i,j)]
            #acceptant?
            if i in Ac1 and j in Ac2:
                Ac.add(I)
            #transitions à partir de cet état
            for c in al1:
                if (i,c) in T1 and (j,c) in T2:
                    a=next(iter(T1[(i,c)]))
                    b=next(iter(T2[(j,c)]))
                    # Est-ce un état connu?
                    if (a,b) in bij:
                        J=bij[(a,b)]
                    else:
                        #Nouvel état
                        k+=1
                        etats.add(k)
                        J=k
                        bij[(a,b)]=k
                        L.append((a,b))
                    T[(I,c)]=J
            #print(L)
        #print("Liste des états :")
        #print([(i,j) for (i,j) in bij])
    return (etats,al1,T,init,Ac)
      
# Trace un cercle de centre (x,y) et de rayon r
def drawCercle(can, x, y, r, coul):
    can.create_oval(x-r, y-r, x+r, y+r, outline=coul)

# Dessine une flèche creuse centré en (x,y) sur un Canvas can
def drawHollowArrow(can, x, y):
    can.create_line(x-25, y-10, x+25, y-10)
    can.create_line(x-25, y+10, x+25, y+10)
    can.create_line(x-25, y-10, x-25, y+10)
    can.create_line(x+25, y-10, x+25, y-15)
    can.create_line(x+25, y+10, x+25, y+15)
    can.create_line(x+25, y-15, x+50, y)
    can.create_line(x+25, y+15, x+50, y)

# Dessine une flèche pointé vers le haut centré en (x,y) sur un Canvas can
def drawTopArrow(can, x, y):
    can.create_line(x, y+15, x, y-15)
    can.create_line(x-5, y-10, x, y-15)
    can.create_line(x+5, y-10, x, y-15)

# Dessine une flèche pointé vers la droite centré en (x,y) sur un Canvas can
def drawRightArrow(can, x, y):
    can.create_line(x-25, y, x+25, y)
    can.create_line(x+20, y-5, x+25, y)
    can.create_line(x+20, y+5, x+25, y)

# Dessine une croix centré en (x,y) sur un Canvas can
def drawCross(can, x, y):
    can.create_line(x-15, y-15, x+15, y+15)
    can.create_line(x-15, y+15, x+15, y-15)

class Table:
    def __init__(self, frame):
        global automate, compl, emond, confirm, valid, determ, deterministe

        (etats_set,alpha_set,transit_dict,init_set,accept_set) = automate
        
        #scrollbar = Scrollbar(frame)
        
        can_table = Canvas(frame, width=(len(alpha_set)+1)*100, height=(len(etats_set)+1)*100) #, scrollregion=(0,0,(len(alpha_set)+1)*100,(len(etats_set)+1)*100)
        #can_table.config(yscrollcommand=scrollbar.set)
        #scrollbar.config( command = can_table.yview )
        
        if transit_dict:
            for (e,l) in transit_dict:
                deterministe = deterministe and (l != '€')
                if not isinstance(transit_dict[(e,l)],set) and transit_dict[(e,l)]:
                    transit_dict[(e,l)] = {transit_dict[(e,l)]}
            entry_width = max(len(v) for v in transit_dict.values())+1
            # si plus d'1 transition possible, l'automate est non déterministe
            deterministe = deterministe and (entry_width-1)==1
        else :
            entry_width = 1
        self.entry = {} # Dictionnaire pour stocker tous les widgets Entry correspondant à leur tuple dans la table de transition
        Canvas(can_table, height=100, width=100, borderwidth=1, relief='solid').grid(row=0, column=1) # Chaque cases du tableau est composé d'un canvas
        Label(can_table, width=1, text="", fg='black', font=('Arial', 16, 'bold')).grid(row=0, column=1) # et d'un label/entry en son centre
        ind_alpha = {} # Dictionnaire { indice de colonne : éléments le l'alphabet }
        ind = 2
        for letter in alpha_set:
            if letter != '€':
                Canvas(can_table, height=100, width=100, borderwidth=1, relief='solid').grid(row=0, column=ind)
                Label(can_table, width=1, text=letter, fg='black', font=('Arial', 16, 'bold')).grid(row=0, column=ind)
                ind_alpha[ind] = letter
                ind+=1
        Canvas(can_table, height=100, width=100, borderwidth=1, relief='solid').grid(row=0, column=ind)
        Label(can_table, width=1, text='€', fg='black', font=('Arial', 16, 'bold')).grid(row=0, column=ind)
        ind_alpha[ind] = '€'
        Canvas(can_table, height=100, width=100).grid(row=0, column=ind+1)
        for etat in etats_set:
            if etat in init_set:
                can_init = Canvas(can_table, height=100, width=100)
                drawHollowArrow(can_init, 40, 50) # dessin de la flêche modélisant le/les etat(s) initial(aux)
                can_init.grid(row=etat, column=0)
            if etat in accept_set:
                can_acc = Canvas(can_table, height=100, width=100, borderwidth=1, relief='solid')
                drawCercle(can_acc, 52, 52, 20, "black") # cercle entourant l'etat ou les etats acceptant(s)
                can_acc.grid(row=etat, column=1)
            else :
                Canvas(can_table, height=100, width=100, borderwidth=1, relief='solid').grid(row=etat, column=1)
            Label(can_table, width=1, text=etat, fg='black', font=('Arial', 16, 'bold')).grid(row=etat, column=1)
            ind=2
            for i in ind_alpha:
                Canvas(can_table, height=100, width=100, borderwidth=1, relief='solid').grid(row=etat, column=ind)
                e = Entry(can_table, width=entry_width, fg='black', font=('Arial', 16, 'bold'))
                e.grid(row=etat, column=ind)
                if ((etat,ind_alpha[ind]) in transit_dict):
                    e.insert(0, str(transit_dict[(etat,ind_alpha[ind])]).replace('{','').replace('}','').replace(' ',''))
                self.entry[(etat,ind_alpha[i])] = e # Ajoutez chaque widget Entry au dictionnaire
                ind+=1
            Canvas(can_table, height=100, width=100).grid(row=etat, column=ind)

        valid = Button(can_table, text="Valider la table\nde transition", command=updateEntries)
        compl = Button(can_table, text="Compléter", command=complet)
        emond = Button(can_table, text="Émonder", command=emonder)
        confirm = Button(can_table, text="Confirmer", command=interfaceRuban)
        determ = Button(can_table, text="Determiniser", command=determinise)

        valid.grid(row=1, column=len(alpha_set)+3, padx=5, pady=3)

        can_table.pack( side = LEFT, fill = BOTH ,expand=True)
        #scrollbar.pack(side = RIGHT, fill=Y )

# Methode de mise a jour de la table de transition
def updateEntries():
    global automate, table
    (etats_set,alpha_set,transit_dict,initial,accept_set) = automate

    # Met à jour le texte de chaque widget Label et propose le bouton completer si l'automate ne l'est pas
    for (etat,letter) in table.entry:
        if table.entry[(etat,letter)].get()!="":
            temp = set(table.entry[(etat,letter)].get().replace('{','').replace('}','').replace(' ','').split(','))
            transit_dict[(etat,letter)] = set()
            for i in temp :
                transit_dict[(etat,letter)].add(int(i))
    # mise à jour de la valeur du champ "table de transition" dans la fenetre principale
    transit_var.set(str(transit_dict))
    # affichage des boutons emonder, completer et confirmer
    valid.grid_remove()
    confirm.grid(row=1, column=len(alpha_set)+3, padx=5, pady=3)
    if deterministe:
        compl.grid(row=2, column=len(alpha_set)+3, padx=5, pady=3)
        emond.grid(row=3, column=len(alpha_set)+3, padx=5, pady=3)
    else :
        determ.grid(row=2, column=len(alpha_set)+3, padx=5, pady=3)
    
# Methode de formatage des donnees et création de la fenetre de la table de transition au clique sur le bouton Confirmer
def createTable():
    global automate, table, table_frame, deterministe
    
    # Verification et conversion des donnees etats, alphabet, etat initial, etat acceptant et table de transition
    try :
        if (transit_var.get()==""):
            transit_dict = {}
        else :
            transit_dict = ast.literal_eval(transit_var.get().replace(' ',''))
    except SyntaxError:
        transit_dict = {}
    # vérification et formatage des états en ensemble
    if (not etats_var.get().isdigit() or int(etats_var.get())<=0):
        messagebox.showerror("Erreur", "Le nombre d'états doit être un entier supérieur à 0")
        return
    else : 
        etats_set = {i for i in range(1,int(etats_var.get())+1)}
    # vérification et formatage des états initiaux en ensemble
    init_temp = set(init_var.get().replace('{','').replace('}','').replace(' ','').split(','))
    init_set = set()
    for i in init_temp:
        if (not i.isdigit()):
            messagebox.showerror("Erreur", "Les états initiaux doivent être des nombres entiers.")
            return
        else :
            init_set.add(int(i))
    # si plus de 1 état initial, l'automate est non déterministe
    deterministe = deterministe and len(init_set)==1
    # vérification et formatage des états acceptants en ensemble
    accept_temp = set(accept_var.get().replace('{','').replace('}','').replace(' ','').split(','))
    accept_set = set()
    for i in accept_temp:
        if (not i.isdigit()):
            messagebox.showerror("Erreur", "Les états acceptants doivent être des entiers séparés d'une virgule.")
            return
        else :
            accept_set.add(int(i))
    alpha_set = set(alpha_var.get().replace('{','').replace('}','').replace('\'','').replace(' ','').split(','))
    
    etat_max = int(etats_var.get())
    if (not max(init_set)<=etat_max or not max(accept_set)<=etat_max):
        messagebox.showerror("Erreur", "Les états acceptants et l'état initial doivent être inférieur ou égal au nombre d'état.")
        return
    
    # Creation d'une nouvelle table de transition
    automate = (etats_set,alpha_set,transit_dict,init_set,accept_set)
    table_frame = Toplevel(fenetre)
    table_frame.title("Table de transition")
    # Crée une nouvelle table dans la nouvelle fenêtre
    table = Table(table_frame)

def selectedAutomate(event=None):
    global etats_var, transit_var, init_var, accept_var, dict_automate, saved_automate

    selection = saved_automate.get()
    etats_var.set(len(dict_automate[selection][0]))
    init_var.set(dict_automate[selection][3])
    accept_var.set(dict_automate[selection][4])
    transit_var.set(dict_automate[selection][2])

def operer():
    global automate, saved_automate,saved_automate2,selectOperation, etats_var, transit_var, init_var, accept_var, alpha_var

    if saved_automate.get()!="" and selectOperation.get()!="":
        aut1 = dict_automate[saved_automate.get()]
        if saved_automate2.get()!="":
            aut2 = dict_automate[saved_automate2.get()]
            if selectOperation.get()=="somme":
                automate = somme(aut1,aut2)
            elif selectOperation.get()=="produit":
                automate = produit(aut1,aut2)
            elif selectOperation.get()=="intersection":
                automate = inter(aut1,aut2)
        else :
            if selectOperation.get()=="plus":
                automate = plus(aut1)
            elif selectOperation.get()=="etoile":
                automate = etoile(aut1)
        etats_var.set(len(automate[0]))
        alpha_var.set(automate[1])
        transit_var.set(automate[2])
        init_var.set(automate[3])
        accept_var.set(automate[4])
        createTable()
    else :
        messagebox.showerror("Erreur", "Opération non valide pour cet/ces automate(s)")

def interfaceOperation():
    global selectOperation,saved_automate2

    btn_operation.grid_remove()
        
    selectOperation.grid(row=0, column=1, padx=5, pady=5)
    saved_automate2.grid(row=0, column=2, padx=5, pady=5)

    btn_operer = Button(saved_automate_frame, text="Opérer", command=operer)
    btn_operer.grid(row=0, column=3, padx=5, pady=5)

# Méthode permettant de sauvegarder un automate
def saveAutomate():
    global saved_automate_frame, saved_automate, saved_automate2, dict_automate, btn_operation, selectOperation

    nom = simpledialog.askstring("Entrez un mot", "Veuillez entrer un nom pour votre automate :", initialvalue="Automate"+str(len(dict_automate)+1))
    if nom is None:
        return # Si l'utilisateur annule la boîte de dialogue, on ne fait rien
    
    if saved_automate_frame and saved_automate_frame.winfo_exists():
        saved_automate_frame.destroy()

    save_btn.grid_remove()

    saved_automate_frame = Frame(fenetre, width=screen_width/3, height=screen_height/3, bg='grey')
    saved_automate_frame.grid(row=1, column=0, padx=10, pady=5)

    selectOperation = ttk.Combobox(saved_automate_frame, state="readonly", values=["plus","etoile"])

    dict_automate[nom]=automate
    btn_operation = Button(saved_automate_frame, text="Effectuer des opérations", command=interfaceOperation)
    btn_operation.grid(row=0, column=1, padx=5, pady=5)

    liste_automates = [nom for nom in dict_automate]
    saved_automate = ttk.Combobox(saved_automate_frame, state="readonly", values = liste_automates)
    saved_automate.current(0)
    saved_automate.grid(row=0, column=0, padx=5, pady=5)
    saved_automate.bind('<<ComboboxSelected>>', selectedAutomate)

    liste_automates.append("")
    saved_automate2 = ttk.Combobox(saved_automate_frame, state="readonly", values = liste_automates)
    saved_automate2.bind('<<ComboboxSelected>>', lambda event: selectOperation.config(values=["plus","etoile"]) if saved_automate2.get() == "" else selectOperation.config(values=["somme","produit","intersection"]))

# Méthode de création de la fenetre du ruban de lecture
def interfaceRuban():
    global down_frame, window_ruban, window_ruban2, mot, automate, fleche_etat, save_btn

    save_btn.grid(row=5, column=0, padx=5, pady=3)

    if window_ruban and window_ruban.winfo_exists():
        window_ruban.destroy()
    if down_frame and down_frame.winfo_exists():
        down_frame.destroy()

    down_frame = Frame(fenetre, width=screen_width/3, height=screen_height/3, bg='grey')
    down_frame.grid(row=2, column=0, padx=10, pady=5)

    # Insertion des widgets de la frame de droite
    Label(down_frame, text="Ruban de lecture").grid(row=0, column=0, padx=5, pady=5)
    frame_word = Frame(down_frame, width=180, height=185)
    frame_word.grid(row=1, column=0, padx=5, pady=5)
    Label(frame_word, text="Entrez un mot :").grid(row=0, column=0, padx=5, pady=5)
    mot = Entry(frame_word)
    mot.grid(row=0, column=1, padx=5, pady=5)
    Button(frame_word, text="Lire", command=lecture).grid(row=0, column=2, padx=5, pady=3)
    window_ruban = Frame(down_frame, height=180, width=400)
    window_ruban.grid(row=2, column=0, padx=10, pady=5)
    window_ruban2 = Frame(down_frame, height=180, width=400)
    window_ruban2.grid(row=3, column=0, padx=10, pady=5)

    # message à l'utilisateur pour le prevenir de la suite de la démarche à suivre
    messagebox.showinfo("C'est prêt !", "Vous pouvez maintenant entrer un mot à lire dans la fenêtre \"Ruban de lecture\".")

def lecture():
    global fleche_etat, deterministe

    # destuction de tous les widgets de la fenetre ruban
    for widget in window_ruban.winfo_children():
        widget.destroy()
    # destuction de tous les widgets de la fenetre ruban
    for widget in window_ruban2.winfo_children():
        widget.destroy()
    
    if deterministe: # on applique la bonne fonction de lecture du mot
        (acc,liste_etat) = lireMot(automate,mot.get())
    else :
        (acc,liste_etat) = lireNDe(automate,mot.get())

    # initialisation à l'état initial du ruban
    init = Canvas(window_ruban, height=50, width=100)
    init.grid(row=1, column=0)
    drawHollowArrow(init, 45,25)
    cerc_init = Canvas(window_ruban, height=50, width=50)
    cerc_init.grid(row=1, column=1)
    drawCercle(cerc_init,27,27,20,"black")
    label_init = Label(window_ruban, text=str(liste_etat[0]).replace('{','').replace('}',''))
    label_init.grid(row=1, column=1)
    lettre_init = Canvas(window_ruban2, height=50, width=50)
    lettre_init.grid(row=0, column=0)
    fleche_etat = Canvas(window_ruban2, height=50, width=50)
    fleche_etat.grid(row=1, column=1)
    drawTopArrow(fleche_etat,25,25)

    # boucle de lecture du mot
    (col,ind) = (3,1)
    for letter in mot.get():
        delay = 700 * (ind+1)
        window_ruban.after(delay, lambda l=letter, c=col, n=liste_etat[ind], fin=(ind==(len(liste_etat)-1)): nextLetter(window_ruban,l,c,n,acc,fin))
        (col,ind) = (col+2,ind+1)
    
# Méthode d'affichage des widgets pour chaque lettre du mot
def nextLetter(window_ruban,letter,col,etat,acc,fin):
    (etats_set,alpha_set,transit_dict,initial,accept_set) = automate
    Label(window_ruban, text=str(letter)).grid(row=0, column=col)
    can = Canvas(window_ruban, height=50, width=100)
    can.grid(row=1, column=col)
    drawRightArrow(can,50,25)
    if fin:
        if acc:
            can_e = Canvas(window_ruban, height=50, width=50, bg="green")
            can_e.grid(row=1, column=col+1)
            Label(window_ruban, text=str(etat).replace('{','').replace('}',''), bg="green", fg="white").grid(row=1, column=col+1)
        else :
            if not etat or etat==0:
                can_e = Canvas(window_ruban, height=50, width=50, bg="red")
                can_e.grid(row=1, column=col+1)
                drawCross(can_e,27,27)
            else:
                can_e = Canvas(window_ruban, height=50, width=50, bg="red")
                can_e.grid(row=1, column=col+1)
                Label(window_ruban, text=str(etat).replace('{','').replace('}',''), bg="red", fg="white").grid(row=1, column=col+1)
        can_l = Canvas(window_ruban2, height=50, width=50, borderwidth=1, relief='solid')
        can_l.grid(row=0, column=col)
        Label(window_ruban2, text=letter).grid(row=0, column=col)
    else :
        can_e = Canvas(window_ruban, height=50, width=50)
        can_e.grid(row=1, column=col+1)
        Label(window_ruban, text=str(etat).replace('{','').replace('}','')).grid(row=1, column=col+1)
        can_l = Canvas(window_ruban2, height=50, width=50, borderwidth=1, relief='solid')
        can_l.grid(row=0, column=col)
        Label(window_ruban2, text=letter).grid(row=0, column=col)
    if etat.intersection(accept_set):
        drawCercle(can_e,27,27,24,"black")
    drawCercle(can_e,27,27,20,"black")
    fleche_etat.grid(row=2, column=col+1)

# nombre total de lignes et de colonnes dans la liste
nb_ligne = len(automate[0])
nb_colonne = len(automate[1])

# Creation de la fenetre principale
fenetre = Tk()
''' Mode plein écran
screen_width = fenetre.winfo_screenwidth()
screen_height = fenetre.winfo_screenheight()
'''
screen_width = 800
screen_height = 750
fenetre.grid_columnconfigure(0, weight=1)
fenetre.geometry(f"{screen_width}x{screen_height}")
fenetre.title("Simulateur d'automate")
fenetre.config(bg="darkgrey")

# Creation de la fenetre du haut
up_frame = Frame(fenetre, width=screen_width/3, height=screen_height/3, bg='grey')
up_frame.grid(row=0, column=0, padx=10, pady=5)

# Insertion des widgets de la frame du haut
Label(up_frame, text="Configuration de l'automate").grid(row=0, column=0, padx=5, pady=5)

tool_bar = Frame(up_frame, width=180, height=185)
tool_bar.grid(row=1, column=0, padx=5, pady=5)

# Association d'une variable StringVar à chaque Entry pour gérer leur mise à jour
etats_var = StringVar()
alpha_var = StringVar()
init_var = StringVar()
accept_var = StringVar()
transit_var = StringVar()

Label(tool_bar, text="Nombre d'états (un entier)").grid(row=0, column=0, padx=5, pady=3)
etats = Entry(tool_bar, textvariable=etats_var)
etats.grid(row=0, column=1, padx=5, pady=5)
Label(tool_bar, text="Alphabet (exemple : a,b)").grid(row=1, column=0, padx=5, pady=5)
alpha = Entry(tool_bar, textvariable=alpha_var)
alpha.grid(row=1, column=1, padx=5, pady=5)
Label(tool_bar, text="Etat initial(aux) ((exemple : 1,2))").grid(row=2, column=0, padx=5, pady=5)
init = Entry(tool_bar, textvariable=init_var)
init.grid(row=2, column=1, padx=5, pady=5)
Label(tool_bar, text="Etat(s) acceptant(s) (exemple : 1,2)").grid(row=3, column=0, padx=5, pady=5)
accept = Entry(tool_bar, textvariable=accept_var)
accept.grid(row=3, column=1, padx=5, pady=5)
Label(tool_bar, text="Table de transition\n(optionnel, exemple : {(1,'a'): {1}, (1,'b'): {1,2}...}").grid(row=4, column=0, padx=5, pady=5)
transit = Entry(tool_bar, textvariable=transit_var)
transit.grid(row=4, column=1, padx=5, pady=5)
save_btn = Button(tool_bar, text="Enregistrer l'automate", command=saveAutomate)
Button(tool_bar, text="Confirmer", command=createTable).grid(row=5, column=1, padx=5, pady=3)

fenetre.mainloop()