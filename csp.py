from typing import Any
from queue import Queue


class CSP:
    def __init__(
        self,
        variables: list[str],
        domains: dict[str, set],
        edges: list[tuple[str, str]],
    ):
        """Constructs a CSP instance with the given variables, domains and edges.
        
        Parameters
        ----------
        variables : list[str]
            The variables for the CSP
        domains : dict[str, set]
            The domains of the variables
        edges : list[tuple[str, str]]
            Pairs of variables that must not be assigned the same value
        """
        self.variables = variables
        self.domains = domains

        # Binary constraints as a dictionary mapping variable pairs to a set of value pairs.
        #
        # To check if variable1=value1, variable2=value2 is in violation of a binary constraint:
        # if (
        #     (variable1, variable2) in self.binary_constraints and
        #     (value1, value2) not in self.binary_constraints[(variable1, variable2)]
        # ) or (
        #     (variable2, variable1) in self.binary_constraints and
        #     (value1, value2) not in self.binary_constraints[(variable2, variable1)]
        # ):
        #     Violates a binary constraint
        self.binary_constraints: dict[tuple[str, str], set] = {}
        for variable1, variable2 in edges:
            self.binary_constraints[(variable1, variable2)] = set()
            for value1 in self.domains[variable1]:
                for value2 in self.domains[variable2]:
                    if value1 != value2:
                        self.binary_constraints[(variable1, variable2)].add((value1, value2))
                        self.binary_constraints[(variable1, variable2)].add((value2, value1))
    def revise(self, Xi, Xj):
        revised = False
        contstraint_frem = self.binary_constraints.get((Xi,Xj), set())
        contstraint_bak = self.binary_constraints.get((Xj,Xi), set())



        for x_verdi in set(self.domains[Xi]):
            godkjent = False #om verdien til Xi er lovlig gitt Xj
            for y_verdi in set (self.domains[Xj]):
                if((x_verdi,y_verdi) in contstraint_frem):
                    godkjent = True
                elif((y_verdi, x_verdi) in contstraint_bak):
                    godkjent = True
            if not godkjent:
                self.domains[Xi].remove(x_verdi)
                revised = True
        return revised
         
    def ac_3(self) -> bool:
        """Performs AC-3 on the CSP.
        Meant to be run prior to calling backtracking_search() to reduce the search for some problems.
        
        Returns
        -------
        bool
            False if a domain becomes empty, otherwise True
        """
        #sikre at man får med alle siden forskjell på rekkefølge
        kø = []
        for(Xi, Xj) in self.binary_constraints:
            kø.append((Xi, Xj))
            kø.append((Xj,Xi))

        while kø:
            (Xi, Xj) = kø.pop()
            if self.revise(Xi, Xj):
                if len(self.domains[Xi])==0:
                    return False
                #finne naboer og legge til
                naboer = set()
                for (A, B) in self.binary_constraints:
                    if A == Xi and B != Xj:
                        naboer.add(B)
                    elif A != Xj and B==Xi:
                        naboer.add(A)
                for Xk in naboer:
                    kø.append((Xk, Xi))
        return True

    def backtracking_search(self) -> None | dict[str, Any]:
        """Performs backtracking search on the CSP.
        
        Returns
        -------
        None | dict[str, Any]
            A solution if any exists, otherwise None
        """
        def backtrack(assignment: dict[str, Any]):
            if len(assignment) == len(self.variables):
                return assignment

            for variable in self.variables:
                if variable not in assignment:
                    var = variable
                    break

            for value in self.domains[var]:
                consistent = True

                for assigned_var in assignment:
                    assigned_value = assignment[assigned_var]

                    if (
                        (assigned_var, var) in self.binary_constraints
                        and (assigned_value, value) not in self.binary_constraints[(assigned_var, var)]
                    ) or (
                        (var, assigned_var) in self.binary_constraints
                        and (value, assigned_value) not in self.binary_constraints[(var, assigned_var)]
                    ):
                        consistent = False
                        break

                if consistent:
                    assignment[var] = value
                    result = backtrack(assignment)

                    if result is not None:
                        return result

                    del assignment[var]

            return None

        return backtrack({})


def alldiff(variables: list[str]) -> list[tuple[str, str]]:
    """Returns a list of edges interconnecting all of the input variables
    
    Parameters
    ----------
    variables : list[str]
        The variables that all must be different

    Returns
    -------
    list[tuple[str, str]]
        List of edges in the form (a, b)
    """
    return [(variables[i], variables[j]) for i in range(len(variables) - 1) for j in range(i + 1, len(variables))]