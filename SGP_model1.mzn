% Use this editor as a MiniZinc scratch book
include "globals.mzn";
include "alldifferent.mzn";

int : nb_golfeurs;
int : nb_semaines;
int : nb_groupes;
int : taille_groupe;

set of int: golfeurs = 1..nb_golfeurs;
set of int: semaines = 1..nb_semaines;
set of int: groupes = 1..nb_groupes;

array[semaines,groupes,1..taille_groupe] of var golfeurs: planning;
array[golfeurs,golfeurs] of var int: rencontres;

%init
constraint taille_groupe=nb_golfeurs/nb_groupes;

%au moins autant de groupes qu'il y a de semaines
%constraint assert(nb_semaines<=nb_groupes,"invalide car il y a trop peu de groupes pour jouer toutes les semaines");
constraint assert(taille_groupe<=nb_groupes,"invalide car la taille du groupe est supérieure au nombre de groupe");
constraint assert(nb_golfeurs mod nb_groupes = 0,"invalide car certains golfeurs n'ont pas de groupes");

%tous les golfeurs jouent chaque semaine
constraint forall(s in semaines)(alldifferent(i in 1..taille_groupe, grp in groupes)(planning[s,grp,i]));

%chaque golfeur n'a été qu'une seule fois avec un autre dans le même groupe
constraint forall(g in golfeurs)(
  forall(s in semaines, grp in groupes, i in 1..taille_groupe where planning[s,grp,i]==g)( % pour chaque groupe où est présent le golfeur
    forall(j in 1..taille_groupe where i!=j)(%on récupère les valeurs des autres golfeurs ayant joué avec
      rencontres[g,planning[s,grp,j]]=sum(ss in semaines, sgrp in groupes, si in 1..taille_groupe, gi in 1..taille_groupe where planning[ss,sgrp,gi]=g)(planning[ss,sgrp,si]=planning[s,grp,j])%la somme de leurs rencontres est placé dans la matrice rencontres
    )
  )
);
constraint forall(x in golfeurs, y in golfeurs)(rencontres[x,y]<=1);

solve satisfy;

output [
        if i=1 then 
          if grp=1 then 
            if s=1 then " \n rencontres est \(rencontres) \n le planning est \n semaine \(s) |\t" else "\n semaine \(s) |\t" endif
          else "\t" endif
        else " " endif ++
        show(planning[s,grp,i])
        |s in semaines, grp in groupes, i in 1..taille_groupe];
