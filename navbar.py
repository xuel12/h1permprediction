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
                 label="Info",
                 children=[
                    dbc.DropdownMenuItem("User Guide", href="/userguide"),
                    dbc.DropdownMenuItem(divider=True),
                    dbc.DropdownMenuItem("About Source Data", href = '/documents'),
                    dbc.DropdownMenuItem(divider=True),
                    dbc.DropdownMenuItem("Data Exploration", href = '/aboutEDA'),
                    dbc.DropdownMenuItem(divider=True),
                    dbc.DropdownMenuItem("About Model Selection", header=True),
                    dbc.DropdownMenuItem("H1B Model", href = '/h1bmodel'),
                    dbc.DropdownMenuItem("PERM Model", href = '/permmodel'),
                    dbc.DropdownMenuItem("Customized Model", href = '/buildmodel'),
                    dbc.DropdownMenuItem(divider=True),
                    dbc.DropdownMenuItem("Contact Us", href = '/contactus'),
                    ],
              ),
            ],
          brand="Home",
          brand_href="/home",
          sticky="top",
        )
     return navbar