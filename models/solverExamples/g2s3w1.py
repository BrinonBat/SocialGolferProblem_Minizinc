Ens=[
# ["P",set({1,2,3,4}),True],

["2",int(2),True],
["3",int(3),True],
["0",set(),True],

["G11",set({1,2,3,4,5,6}),False],
["G12",set({1,2,3,4,5,6}),False],
# ["G21",set({1,2,3,4,5,6}),False],
# ["G22",set({1,2,3,4,5,6}),False],


["G11nG12",set({1,2,3,4,5,6}),False],
# ["G11nG21",set({1,2,3,4,5,6}),False],
# ["G21nG22",set({1,2,3,4,5,6}),False],
# ["G12nG22",set({1,2,3,4,5,6}),False],
# ["G11nG22",set({1,2,3,4,5,6}),False],
# ["G12nG21",set({1,2,3,4,5,6}),False],

]


Cstr=[
["cardeq","G11","3"],
["cardeq","G12","3"],
# ["cardeq","G21","3"],
# ["cardeq","G22","3"],

["intersect","G11","G12","G11nG12"],
# ["intersect","G11","G21","G11nG21"],
# ["intersect","G21","G22","G21nG22"],
# ["intersect","G12","G22","G12nG22"],
# ["intersect","G11","G22","G11nG22"],
# ["intersect","G12","G21","G12nG21"],

["equals","G11nG12","0"],
# ["equals","G21nG22","0"],
# ["cardlt","G11nG21","2"],
# ["cardlt","G12nG22","2"],
# ["cardlt","G12nG21","2"],
# ["cardlt","G11nG22","2"]
]