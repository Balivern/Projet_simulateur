from tkinter import *
from tkinter import messagebox
import ast

# donnees par defaut a afficher dans la table de transition
global automate, window_ruban, table_frame

window_ruban = None
frame = None
table_frame = None

etats_set = set()
alpha_set = set()
transit_dict = {}
initial = 1
accept_set = set()
automate = (etats_set,alpha_set,transit_dict,initial,accept_set)

def lireMot(aut,m):
    (etats,alpha,transit,init,acceptant)=aut
    lecture=[init]
    suivant=init
    for j in m:
        if (suivant,j) in transit:
            suivant=transit[(suivant,j)]
            lecture.append(suivant)
        else:
            lecture.append(0)
            return (False,lecture)
    return (suivant in acceptant,lecture)

def complet():
    global automate, table, table_frame

    (etats_set,alpha_set,transit_dict,initial,accept_set) = automate
    
    # Met à jour le texte de chaque widget Label
    for (etat,letter) in table.entry:
        if table.entry[(etat,letter)].get()!="":
            transit_dict[(etat,letter)] = int(table.entry[(etat,letter)].get())
    # mise à jour de la valeur du champ "table de transition" dans la fenetre principale
    
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
        j=T[i,c]
        if i in C and j in C:
            T2[(bij[i],c)]=bij[j]
                
    etats_var.set(str(max(etats2)))
    transit_var.set(str(T2))
    init_var.set(str(bij[init]))
    accept_var.set(str(Ac2)[slice(1,len(str(Ac2))-1)])
    automate = (etats2,alpha,T2,bij[init],Ac2 )

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
                j=T[(i,c)]
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
    Access={init} # joue le rôle de visite
    L=[init]
    while L:
        i=L.pop(0)
        for c in alpha:
            if (i,c) in T:
                j=T[(i,c)]
                if not j in Access:
                    Access.add(j)
                    L.append(j)
    return Access            

# Trace un cercle de centre (x,y) et de rayon r
def draw_cercle(can, x, y, r, coul):
    can.create_oval(x-r, y-r, x+r, y+r, outline=coul)

# Dessine une flèche creuse centré en (x,y) sur un Canvas can
def draw_hollow_arrow(can, x, y):
    can.create_line(x-25, y-10, x+25, y-10)
    can.create_line(x-25, y+10, x+25, y+10)
    can.create_line(x-25, y-10, x-25, y+10)
    can.create_line(x+25, y-10, x+25, y-15)
    can.create_line(x+25, y+10, x+25, y+15)
    can.create_line(x+25, y-15, x+50, y)
    can.create_line(x+25, y+15, x+50, y)

# Dessine une flèche pointé vers le haut centré en (x,y) sur un Canvas can
def draw_top_arrow(can, x, y):
    can.create_line(x, y+15, x, y-15)
    can.create_line(x-5, y-10, x, y-15)
    can.create_line(x+5, y-10, x, y-15)

# Dessine une flèche pointé vers la droite centré en (x,y) sur un Canvas can
def draw_right_arrow(can, x, y):
    can.create_line(x-25, y, x+25, y)
    can.create_line(x+20, y-5, x+25, y)
    can.create_line(x+20, y+5, x+25, y)

# Dessine une croix centré en (x,y) sur un Canvas can
def draw_cross(can, x, y):
    can.create_line(x-15, y-15, x+15, y+15)
    can.create_line(x-15, y+15, x+15, y-15)

class Table:
    def __init__(self, frame):
        global automate, compl, emond, confirm, valid
        (etats_set,alpha_set,transit_dict,initial,accept_set) = automate
        self.entry = {} # Dictionnaire pour stocker tous les widgets Entry correspondant à leur tuple dans la table de transition
        Canvas(frame, height=100, width=100, borderwidth=1, relief='solid').grid(row=0, column=1) # Chaque cases du tableau est composé d'un canvas
        Label(frame, width=1, text="", fg='black', font=('Arial', 16, 'bold')).grid(row=0, column=1) # et d'un label/entry en son centre
        ind_alpha = {} # Dictionnaire { indice de colonne : éléments le l'alphabet }
        ind = 2
        for letter in alpha_set:
            Canvas(frame, height=100, width=100, borderwidth=1, relief='solid').grid(row=0, column=ind)
            Label(frame, width=1, text=letter, fg='black', font=('Arial', 16, 'bold')).grid(row=0, column=ind)
            ind_alpha[ind] = letter
            ind+=1
        Canvas(frame, height=100, width=100).grid(row=0, column=ind)
        for etat in etats_set:
            if etat==initial:
                can_init = Canvas(frame, height=100, width=100)
                draw_hollow_arrow(can_init, 40, 50) # dessin de la flêche modélisant le/les etat(s) initial(aux)
                can_init.grid(row=etat, column=0)
            if etat in accept_set:
                can_acc = Canvas(frame, height=100, width=100, borderwidth=1, relief='solid')
                draw_cercle(can_acc, 52, 52, 20, "black") # cercle entourant l'etat ou les etats acceptant(s)
                can_acc.grid(row=etat, column=1)
            else :
                Canvas(frame, height=100, width=100, borderwidth=1, relief='solid').grid(row=etat, column=1)
            Label(frame, width=1, text=etat, fg='black', font=('Arial', 16, 'bold')).grid(row=etat, column=1)
            ind=2
            for i in ind_alpha:
                Canvas(frame, height=100, width=100, borderwidth=1, relief='solid').grid(row=etat, column=ind)
                e = Entry(frame, width=1, fg='black', font=('Arial', 16, 'bold'))
                e.grid(row=etat, column=ind)
                if ((etat,ind_alpha[ind]) in transit_dict):
                    e.insert(0, str(transit_dict[(etat,ind_alpha[ind])]))
                self.entry[(etat,ind_alpha[i])] = e # Ajoutez chaque widget Entry au dictionnaire
                ind+=1
            Canvas(frame, height=100, width=100).grid(row=etat, column=ind)

        valid = Button(frame, text="Valider la table\nde transition", command=update_entries)
        compl = Button(frame, text="Compléter", command=complet)
        emond = Button(frame, text="Émonder", command=emonder)
        confirm = Button(frame, text="Confirmer", command=interface_ruban)

        valid.grid(row=len(etats_set)+2, column=len(alpha_set)+1, padx=5, pady=3)

# Methode de mise a jour de la table de transition
def update_entries():
    global automate, table
    (etats_set,alpha_set,transit_dict,initial,accept_set) = automate

    # Met à jour le texte de chaque widget Label et propose le bouton completer si l'automate ne l'est pas
    for (etat,letter) in table.entry:
        if table.entry[(etat,letter)].get()!="":
            transit_dict[(etat,letter)] = int(table.entry[(etat,letter)].get())
    # mise à jour de la valeur du champ "table de transition" dans la fenetre principale
    transit_var.set(str(transit_dict))
    #affichage des boutons emonder, completer et confirmer
    valid.grid_remove()
    compl.grid(row=len(etats_set)+2, column=len(alpha_set)-1, padx=5, pady=3)
    emond.grid(row=len(etats_set)+2, column=len(alpha_set), padx=5, pady=3)
    confirm.grid(row=len(etats_set)+2, column=len(alpha_set)+1, padx=5, pady=3)

# Methode de formatage des donnees et création de la fenetre de la table de transition au clique sur le bouton Confirmer
def create_table():
    global automate, table, table_frame
    
    # Verification et conversion des donnees etats, alphabet, etat initial, etat acceptant et table de transition
    if (transit.get()==""):
        transit_dict = {}
    else :
        transit_dict = ast.literal_eval(transit.get())

    if (not etats_var.get().isdigit() or int(etats_var.get())<=0):
        messagebox.showerror("Erreur", "Le nombre d'états doit être un entier supérieur à 0")
        return
    if (not init_var.get().isdigit()):
        messagebox.showerror("Erreur", "L'état initial doit être un nombre entier.")
        return
    accept_temp = set(accept_var.get().split(','))
    accept_set = set()
    for i in accept_temp:
        if (not i.isdigit()):
            messagebox.showerror("Erreur", "Les états acceptants doivent être des entiers séparés d'une virgule.")
            return
        else :
            accept_set.add(int(i))
    etats_set = {i for i in range(1,int(etats_var.get())+1)}
    alpha_set = set(alpha.get().split(','))
    initial = int(init_var.get())
    
    etat_max = int(etats_var.get())
    if (not initial<=etat_max or not max(accept_set)<=etat_max):
        messagebox.showerror("Erreur", "Les états acceptants et l'état initial doivent être inférieur ou égal au nombre d'état.")
        return
    
    # Creation d'une nouvelle table de transition
    automate = (etats_set,alpha_set,transit_dict,initial,accept_set)
    table_frame = Toplevel(fenetre)
    table_frame.title("Table de transition")
    # Crée une nouvelle table dans la nouvelle fenêtre
    table = Table(table_frame)

# Méthode de création de la fenetre du ruban de lecture   
def interface_ruban():
    global down_frame, window_ruban, window_ruban2, mot, automate, fleche_etat

    if window_ruban and window_ruban.winfo_exists():
        window_ruban.destroy()

    down_frame = Frame(fenetre, width=screen_width/3, height=screen_height/3, bg='grey')
    down_frame.grid(row=1, column=0, padx=10, pady=5)

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
    global fleche_etat

    # destuction de tous les widgets de la fenetre ruban
    for widget in window_ruban.winfo_children():
        widget.destroy()
    # destuction de tous les widgets de la fenetre ruban
    for widget in window_ruban2.winfo_children():
        widget.destroy()
    
    (acc,liste_etat) = lireMot(automate,mot.get())

    # initialisation à l'état initial du ruban
    init = Canvas(window_ruban, height=50, width=100)
    init.grid(row=1, column=0)
    draw_hollow_arrow(init, 45,25)
    cerc_init = Canvas(window_ruban, height=50, width=50)
    cerc_init.grid(row=1, column=1)
    draw_cercle(cerc_init,27,27,20,"black")
    label_init = Label(window_ruban, text=str(liste_etat[0]))
    label_init.grid(row=1, column=1)
    lettre_init = Canvas(window_ruban2, height=50, width=50)
    lettre_init.grid(row=0, column=0)
    fleche_etat = Canvas(window_ruban2, height=50, width=50)
    fleche_etat.grid(row=1, column=1)
    draw_top_arrow(fleche_etat,25,25)

    # boucle de lecture du mot
    (col,ind) = (3,1)
    for letter in mot.get():
        delay = 700 * (ind+1)
        window_ruban.after(delay, lambda l=letter, c=col, n=liste_etat[ind], fin=(ind==(len(liste_etat)-1)): next_letter(window_ruban,l,c,n,acc,fin))
        (col,ind) = (col+2,ind+1)
    
# Méthode d'affichage des widgets pour chaque lettre du mot
def next_letter(window_ruban,letter,col,etat,acc,fin):
    (etats_set,alpha_set,transit_dict,initial,accept_set) = automate
    Label(window_ruban, text=str(letter)).grid(row=0, column=col)
    can = Canvas(window_ruban, height=50, width=100)
    can.grid(row=1, column=col)
    draw_right_arrow(can,50,25)
    if fin:
        if acc:
            can_e = Canvas(window_ruban, height=50, width=50, bg="green")
            can_e.grid(row=1, column=col+1)
            Label(window_ruban, text=str(etat), bg="green", fg="white").grid(row=1, column=col+1)
        else :
            if etat==0:
                can_e = Canvas(window_ruban, height=50, width=50, bg="red")
                can_e.grid(row=1, column=col+1)
                draw_cross(can_e,27,27)
            else:
                can_e = Canvas(window_ruban, height=50, width=50, bg="red")
                can_e.grid(row=1, column=col+1)
                Label(window_ruban, text=str(etat), bg="red", fg="white").grid(row=1, column=col+1)
        can_l = Canvas(window_ruban2, height=50, width=50, borderwidth=1, relief='solid')
        can_l.grid(row=0, column=col)
        Label(window_ruban2, text=letter).grid(row=0, column=col)
    else :
        can_e = Canvas(window_ruban, height=50, width=50)
        can_e.grid(row=1, column=col+1)
        Label(window_ruban, text=str(etat)).grid(row=1, column=col+1)
        can_l = Canvas(window_ruban2, height=50, width=50, borderwidth=1, relief='solid')
        can_l.grid(row=0, column=col)
        Label(window_ruban2, text=letter).grid(row=0, column=col)
    if etat in accept_set:
        draw_cercle(can_e,27,27,24,"black")
    draw_cercle(can_e,27,27,20,"black")
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
init_var = StringVar()
accept_var = StringVar()
transit_var = StringVar()

Label(tool_bar, text="Nombre d'états (un entier)").grid(row=0, column=0, padx=5, pady=3)
etats = Entry(tool_bar, textvariable=etats_var)
etats.grid(row=0, column=1, padx=5, pady=5)
Label(tool_bar, text="Alphabet (exemple : a,b)").grid(row=1, column=0, padx=5, pady=5)
alpha = Entry(tool_bar)
alpha.grid(row=1, column=1, padx=5, pady=5)
Label(tool_bar, text="Etat initial (un entier)").grid(row=2, column=0, padx=5, pady=5)
init = Entry(tool_bar, textvariable=init_var)
init.grid(row=2, column=1, padx=5, pady=5)
Label(tool_bar, text="Etat(s) acceptant(s) (exemple : 1,2)").grid(row=3, column=0, padx=5, pady=5)
accept = Entry(tool_bar, textvariable=accept_var)
accept.grid(row=3, column=1, padx=5, pady=5)
Label(tool_bar, text="Table de transition\n(optionnel, exemple : {(1,'a': 1), (1,'b': 1)}").grid(row=4, column=0, padx=5, pady=5)
transit = Entry(tool_bar, textvariable=transit_var)
transit.grid(row=4, column=1, padx=5, pady=5)
Button(tool_bar, text="Confirmer", command=create_table).grid(row=5, column=1, padx=5, pady=3)

fenetre.mainloop()