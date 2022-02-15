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
constraint forall(semaine in semaines) ( array_union([planning[semaine,groupe]| groupe in groupes])=golfeurs);

% les groupes sont de taille nb_golfeurs/nb_groupes
constraint forall(semaine in semaines, groupe in groupes)(card(planning[semaine,groupe])=taille_groupes);

% chaque golfeur ne joue qu'une seule fois avec chaque autre
constraint forall(s1,s2 in semaines, g1,g2 in groupes where {s1,g1}!={s2,g2})(
  card(planning[s1,g1] intersect planning[s2,g2])<=1
);

%assertions
constraint assert(taille_groupes <= nb_groupes,"invalide car la taille du groupe est supérieure au nombre de groupe");

%brisage de symmetrie
constraint forall(groupe in groupes)(
  planning[1,groupe]=((groupe-1)*taille_groupes+1)..(groupe*taille_groupes)
);

%temp, à remplacer par la contrainte du pourquoi quand retirage de solution est identifié, notamment pour groupes de taille 2
%constraint forall(semaine in semaines)( 1 in planning[semaine,1]);
%constraint forall(semaine in 2..nb_semaines) (2 in planning[semaine,2]);

% CONTRAINTE DU POURQUOI 
constraint forall(groupe_number in 1..nb_groupes-1)(
  forall(semaine in groupe_number..nb_semaines) ( groupe_number in planning[semaine,groupe_number])
);
solve satisfy;

output [ if grp=1 then "\n semaine \(s) |\t" else " \t" endif
        ++ show(planning[s,grp])|s in semaines, grp in groupes];