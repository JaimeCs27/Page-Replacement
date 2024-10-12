from mmu import MMU

instructions = [("new", 1, 1), # 1 = 2
                ("new", 2, 1), # 2 = 3
                ("new", 3, 1), # 3 = 4
                ("use", 1),    # 2
                ("new", 4, 1), # 4 = 1
                ("use", 2),    # 3
                ("new", 5, 1), # 5 = 7
                ("new", 6, 1), # 6 = 5
                ("use", 3),    # 4
                ("use", 2),]    # 3
mmu = MMU("OPT", instructions)
mmu.new(1, 1)
mmu.new(2, 1)
mmu.new(3, 1)
mmu.use(1)
mmu.new(4, 1)
mmu.use(2)
mmu.new(5, 1)
mmu.new(6, 1)
mmu.use(3)
mmu.use(2)
print("MMU1: " + str(mmu.clock))
mmu.printRam()
mmu2 = MMU("MRU", instructions)
mmu2.new(1, 1)
mmu2.new(2, 1)
mmu2.new(3, 1)
mmu2.use(1)
mmu2.new(4, 1)
mmu2.use(2)
mmu2.new(5, 1)
mmu2.new(6, 1)
mmu2.use(3)
mmu2.use(2)
print("MMU2: " + str(mmu2.clock))
mmu2.printRam()