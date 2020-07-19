import dash_bootstrap_components as dbc
def Navbar():
     navbar = dbc.NavbarSimple(
           children=[
              dbc.NavItem(dbc.NavLink("Explore H-1B Data", href="/eda")),
              dbc.NavItem(dbc.NavLink("Explore PERM Data", href="/eda_perm")),
              dbc.NavItem(dbc.NavLink("Update H-1B Dataset", href="/training")),
              dbc.NavItem(dbc.NavLink("Update PERM Dataset", href="/training_perm")),
              dbc.DropdownMenu(
                 nav=True,
                 in_navbar=True,
                 label="Menu",
                 children=[
                    dbc.DropdownMenuItem("Entry 1"),
                    dbc.DropdownMenuItem("Entry 2"),
                    dbc.DropdownMenuItem(divider=True),
                    dbc.DropdownMenuItem("Entry 3"),
                          ],
                      ),
                    ],
          brand="Home",
          brand_href="/home",
          sticky="top",
        )
     return navbar