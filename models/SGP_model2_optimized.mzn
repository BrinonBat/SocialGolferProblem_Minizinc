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

%assertions
%A1
constraint assert(taille_groupes <= nb_groupes,"invalide car la taille du groupe est supérieure au nombre de groupe");

%surcontraintes
%Un joueur ne joue qu'une seule fois par semaine
%C4
%constraint forall(semaine in semaines, g1,g2 in groupes where g1!=g2)(
%  card(planning[semaine,g1] intersect planning[semaine,g2])=0
%);

%C5
%constraint forall(semaine in semaines, g1,g2 in groupes where g1!=g2)(
%  planning[semaine,g1] intersect planning[semaine,g2] = {}
%);


%brisage de symmetrie
%contrainte sur la première ligne
%C6
constraint forall(groupe in groupes)(
  planning[1,groupe]=((groupe-1)*taille_groupes+1)..(groupe*taille_groupes)
);

%contrainte sur la répartition d'une semaine de la première semaine parmi les semaines suivantes
%C7
constraint forall( golfeur in 1..taille_groupes)(
 forall(semaine in 2..nb_semaines)(
    golfeur in planning[semaine,golfeur]
  )
);

solve satisfy;

output [ if grp=1 then "\n semaine \(s) |\t" else "\t" endif
        ++ show(planning[s,grp])|s in semaines, grp in groupes];