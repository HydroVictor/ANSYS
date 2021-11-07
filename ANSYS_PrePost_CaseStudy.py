# Access to the analysis/geometry
analysis = ExtAPI.DataModel.Project.Model.Analyses[0]
geometry = ExtAPI.DataModel.Project.Model.Geometry
Named_Selections = ExtAPI.DataModel.Project.Model.NamedSelections.Children


# Set Isometric View
Graphics.Camera.FocalPoint = Point([0.496249, -0.495000, 4.209571], 'm')
Graphics.Camera.ViewVector = Vector3D(0.57735, 0.57735, 0.57735)
Graphics.Camera.UpVector = Vector3D(-0.408248, 0.816497, -0.408248)
Graphics.Camera.SceneHeight = Quantity(12.013655, 'm')
Graphics.Camera.SceneWidth = Quantity(12.916089, 'm')

# Zoom to fit
Graphics.Camera.FocalPoint = Point([0.000000, -0.980750, 4.231971], 'm')
Graphics.Camera.ViewVector = Vector3D(0.57735, 0.57735, 0.57735)
Graphics.Camera.UpVector = Vector3D(-0.408248, 0.816497, -0.408248)
Graphics.Camera.SceneHeight = Quantity(3.142182, 'm')
Graphics.Camera.SceneWidth = Quantity(2.407493, 'm')

# Display Style - Visible Thickness
geometry.DisplayStyle = PrototypeDisplayStyleType.VisibleThickness
# Create image in Model tree
Figure_1 = ExtAPI.DataModel.Project.Model.Geometry.AddFigure()
Image_1 = ExtAPI.DataModel.Project.Model.Geometry.AddImage()
Figure_1.Name = "Full geometry (visible thickness)"
Image_1.Name = "Full geometry (visible thickness)"

# Display Style - Material
geometry.DisplayStyle = PrototypeDisplayStyleType.Material
# Create image in Model tree
Figure_2 = ExtAPI.DataModel.Project.Model.Geometry.AddFigure()
Image_2 = ExtAPI.DataModel.Project.Model.Geometry.AddImage()
Figure_2.Name = "Full geometry (material)"
Image_2.Name = "Full geometry (material)"


time = 1 # Time step to plot
n_steps = 2 # Number of time steps

# Addressing to analysis settings
analysis_settings = ExtAPI.DataModel.Project.Model.Analyses[0].AnalysisSettings

# Solver Controls
analysis_settings.SolverType = SolverType.Direct

# Output Controls
analysis_settings.NodalForces = OutputControlsNodalForcesType.Yes

# Step Controls
analysis_settings.NumberOfSteps = n_steps
for i_step in range(n_steps + 1):
	if i_step == 0:
		continue
	if i_step == 1:
		analysis_settings.SetAutomaticTimeStepping(i_step, AutomaticTimeStepping.On)
		analysis_settings.SetInitialSubsteps(i_step, 5)
		analysis_settings.SetMinimumSubsteps(i_step, 1)
		analysis_settings.SetMaximumSubsteps(i_step, 10)
	else:
		analysis_settings.SetAutomaticTimeStepping(i_step, AutomaticTimeStepping.On)
		analysis_settings.SetInitialSubsteps(i_step, 10)
		analysis_settings.SetMinimumSubsteps(i_step, 10)
		analysis_settings.SetMaximumSubsteps(i_step, 20)


wear_1mm = 1
wear_1mm_mass = 7.85e-6

wear_2mm = 2
wear_2mm_mass = 15.7e-6

isolation_mass = 19.5e-6
pressure_MPa = 2e-2


# Wear and Isolation
isolation = geometry.AddDistributedMass()
isolation.MassType = DistributedMassInputType.MassPerUnitArea
isolation.MassPerUnitArea = Quantity(isolation_mass, "kg mm^-1 mm^-1")
# ----------Create Named Selection "Isolierung" in advance
nsel_Isolation = [i for i in Named_Selections if i.Name=='Isolierung'][0]
isolation.Location = nsel_Isolation
isolation.Name = nsel_Isolation.Name

for i in Named_Selections:
	if i.Name=='Verschleiss_2mm':
		wear2 = geometry.AddDistributedMass()
		wear2.MassType = DistributedMassInputType.MassPerUnitArea
		wear2.MassPerUnitArea = Quantity(wear_2mm_mass, "kg mm^-1 mm^-1")
		# ----------Create Named Selection "Verschleiss_2mm" in advance
		nsel_wear_2mm = i
		wear2.Location = nsel_wear_2mm
		wear2.Name = nsel_wear_2mm.Name
	elif i.Name=='Verschleiss_1mm':
		wear1 = geometry.AddDistributedMass()
		wear1.MassType = DistributedMassInputType.MassPerUnitArea
		wear1.MassPerUnitArea = Quantity(wear_1mm_mass, "kg mm^-1 mm^-1")
		# ----------Create Named Selection "Verschleiss_1mm" in advance
		nsel_wear_1mm = i
		wear1.Location = nsel_wear_1mm
		wear1.Name = nsel_wear_1mm.Name


# Loads
gravity = analysis.AddEarthGravity()
gravity.Direction = GravityOrientationType.NegativeYAxis

# Pressure
pressure = analysis.AddPressure()
# ----------Create Named Selection "Pressure" for 0,2 bat in advance
nsel_Pressure = [i for i in Named_Selections if i.Name=='Pressure'][0]
pressure.Location = nsel_Pressure
pressure.Name = "Pressure"
pressure.DefineBy = LoadDefineBy.ComplexNormalTo
pressure.Magnitude.Inputs[0].DiscreteValues=[
				Quantity('0[sec]'), 
				Quantity('1[sec]'),
				Quantity('2[sec]')]
pressure.Magnitude.Output.DiscreteValues=[
				Quantity('0 [MPa]'),
				Quantity('{} [MPa]'.format(pressure_MPa)), 
				Quantity('{} [MPa]'.format(pressure_MPa*2))
				]


# Start SOLVER
analysis.Solve(True)



time = 1 #Time step to plot

# Reading results
results = ExtAPI.DataModel.Project.Model.Analyses[0].Solution

# Plot - epto1 
epto1 = results.AddUserDefinedResult()
epto1.Expression = r'epto1'
epto1.AverageAcrossBodies = True
epto1.DisplayTime = Quantity(time, "sec")
epto1.Name = 'epto1 - {} s'.format(time)
epto1.EvaluateAllResults()

# Plot - epto3 
epto3 = results.AddUserDefinedResult()
epto3.Expression = r'-epto3'
epto3.AverageAcrossBodies = True
epto3.DisplayTime = Quantity(time, "sec")
epto3.Name = '-epto3 - {} s'.format(time)
epto3.EvaluateAllResults()

# Plot - epto1 (keine Rippen)
epto1_keineRippen = results.AddUserDefinedResult()
epto1_keineRippen.Expression = r'epto1'
epto1_keineRippen.Name = 'epto1 (keine Rippen) - {} s'.format(time)
# ----------Create Named Selection "Mantelblech" in advance in Mechanical
nsel_Mantelblech = [i for i in ExtAPI.DataModel.Project.Model.NamedSelections.Children if i.Name=="Mantelblech"][0]
epto1_keineRippen.Location = nsel_Mantelblech
epto1_keineRippen.AverageAcrossBodies = True
epto1_keineRippen.DisplayTime = Quantity(time,"sec")
epto1_keineRippen.EvaluateAllResults()

# Plot - Total Deformation
TotalDeformation = results.AddTotalDeformation()
TotalDeformation.DisplayTime = Quantity(time, "sec")
TotalDeformation.Name = 'Total Deformation - {} s'.format(time)
TotalDeformation.EvaluateAllResults()

# Plot - Eq.Stress
EqStress = results.AddEquivalentStress()
EqStress.DisplayTime = Quantity(time,"sec")
EqStress.Name = 'Equivalent Stress - {} s'.format(time)
EqStress.EvaluateAllResults()