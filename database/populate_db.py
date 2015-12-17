from db import db, Manufacturer, Model
import json


def main():
    with open("planes.json") as j:
        d = json.load(j)
    for manufacturer in d:
        man = Manufacturer(manufacturer)
        db.session.add(man)
        db.session.commit()
        for model in d[manufacturer]:
            mod = Model(model,
                        d[manufacturer][model]["Description"],
                        d[manufacturer][model]["Pic"])
            man.models.append(mod)
        db.session.commit()

if __name__ == "__main__":
    main()
