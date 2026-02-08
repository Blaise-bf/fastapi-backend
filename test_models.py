from models import CarModel, CarCollection, UpdateCarModel

test_car = CarModel(brand='ford', make='fiesta', year=2019, cm3=1500, km=120000, price=10000)
test_car1 = CarModel(brand='fiat', make='stilo', year=2003, cm3=1600, km=320000, price=3000)

car_list = CarCollection(cars=[test_car, test_car1])

print(car_list.model_dump())