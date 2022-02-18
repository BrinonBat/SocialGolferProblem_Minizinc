int: players;
int: groups;
int: weeks;
int: groupSize = players div groups;

set of int: P = 1..players;
set of int: G = 1..groups;
set of int: W = 1..weeks;

array[W,G] of var set of P: WG;
  
  % All groups are the right size (0)
constraint forall(w in W, g in G)(card(WG[w,g])=groupSize);
  
  % Every Week, All Players play (1)
constraint forall(w in W)(
  array_union([WG[w,g] | g in G])=P
);

  % No Two Groups have more than one common Player (2)
constraint forall(w1,w2 in W, g1,g2 in G where [w1,g1]!=[w2,g2])(
  card(WG[w1,g1] intersect WG[w2,g2]) <= 1
);



% Extra Constraints
  %A player doesn't play in two groups / Twice, the same week (E1) % This constraint is achived by (1+2)
  %by restricting the card of the intersect (E1a)
constraint forall(w in W, g1,g2 in G where g1!=g2)(
  card(WG[w,g1] intersect WG[w,g2])=0
);
  %by restricting the set of the intersect (E1b)
constraint forall(w in W, g1,g2 in G where g1!=g2)(
  WG[w,g1] intersect WG[w,g2] = {}
);





% Symmetry Breaking
  % The first week is {1..groupSize}, {groupSize+1..2*groupSize}, etc..
constraint forall(i in P)(
	i in WG[1, ((i-1) div groupSize)+1]
);

  % Split First Group of First Week
  %using first Week Constraint
constraint let { var set of int: FGFW = 1..groupSize} in
  forall(p in FGFW, w in W diff {1})(
    p in WG[w,p]
);

  %general
% constraint let { var set of int: FGFW = WG[1,1]} in
%   forall(p in FGFW, w in W diff {1})(
%     p in WG[w,p]
% );



solve satisfy;



output [ if grp=1 then "\n semaine \(s) |\t" else "\t" endif
        ++ show(WG[s,grp])|s in W, grp in G];