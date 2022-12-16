# IOC ACCESS SECURITY FILE

# full write and read access
# 
ASG(default) {
    RULE(1, READ)
    RULE(1, WRITE)
}

# read-only PVs
# 
ASG(readonly) {
    RULE(1, READ)
    RULE(0, WRITE)
}

# ASG(rbpv) {
#     RULE(1, READ)
#     RULE(0, WRITE)
# }
