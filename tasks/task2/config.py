from common.calculation.interpolation.interpolators.lagrangian_interpolator import LagrangianInterpolator
from common.calculation.interpolation.interpolators.newton_interpolator import NewtonInterpolator
from common.models.point_generation import RandomPointGenerator, EquidistantPointGenerator

INTERPOLATORS = {
    LagrangianInterpolator.name: LagrangianInterpolator(),
    NewtonInterpolator.name: NewtonInterpolator(),
}

POINT_GENERATORS = {
    RandomPointGenerator.name: RandomPointGenerator(),
    EquidistantPointGenerator.name: EquidistantPointGenerator(),
}
