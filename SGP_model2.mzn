include "globals.mzn";
include "alldifferent.mzn";

int : taille_groupes;
int : nb_groupes;
int : nb_semaines;

set of int: golfeurs = 1..taille_groupes*nb_groupes;
set of int: semaines = 1..nb_semaines;
set of int: groupes = 1..nb_groupes;

array[semaines,groupes] of var set of golfeurs: planning;

% tous les joueurs jouent chaque semaine
%C1
constraint forall(semaine in semaines) ( array_union([planning[semaine,groupe]| groupe in groupes])=golfeurs);

% les groupes sont de taille nb_golfeurs/nb_groupes
%C2
constraint forall(semaine in semaines, groupe in groupes)(card(planning[semaine,groupe])=taille_groupes);

% chaque golfeur ne joue qu'une seule fois avec chaque autre
%C3
constraint forall(s1,s2 in semaines, g1,g2 in groupes where [s1,g1]!=[s2,g2])(
  card(planning[s1,g1] intersect planning[s2,g2])<=1
);

solve satisfy;

output [ if grp=1 then "\n semaine \(s) |\t" else " \t" endif
        ++ show(planning[s,grp])|s in semaines, grp in groupes];