# AI Meeting point selector

Algo approach:  
J(x) = sum(t_i(x)) + alpha * N * MAD(t_i(x)) + beta * N * max(t_i(x))  
  
where:  
t_i(x) = travel time from traveler i to candidate location x  
N = number of participants  
  
TODOS:
- Get API set up
- Implement MAD(t_i(x)) in place of pstdev
- Set alpha and beta parameters
