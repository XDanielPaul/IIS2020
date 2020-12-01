import click
from flask.cli import with_appcontext
from .models import User,Festival,Reservation,Ticket,Stage,Interpret, Schedule, Performance, perfs
from .extensions import db

@click.command(name='create_tables')
@with_appcontext
def create_tables():
    db.create_all()

@click.command(name='destroy_tables')
@with_appcontext
def destroy_tables():
    db.drop_all()

@click.command(name='restart_tables')
@with_appcontext
def restart_tables():
    db.drop_all()
    db.create_all()

@click.command(name='fill_database')
@with_appcontext
def fill_database():
    #USERS
    db.session.add(User(name = "Nadmin", surname = "Sadmin", login = "admin", email="admin@gmail.com", unhashed_password= "admin", priviliges = 3))
    db.session.add(User(name = "Norganizer", surname = "Soranizer", email="organizer@organizer.com", login = "organizer", unhashed_password= "organizer", priviliges = 2))
    db.session.add(User(name = "Ncashier", surname = "Scashier", email="cashier@cashier.com", login = "cashier", unhashed_password= "cashier", priviliges = 1))
    db.session.add(User(name = "Nuser", surname = "Suser", email="user@user.com", login = "user", unhashed_password= "user", priviliges = 0))
    db.session.commit()
    #----------
    
    #FESTIVALS
    f_pohoda = Festival(name="Pohoda", description="Pohoda is the most famous Slovak multi-genre festival. For its line-up and atmosphere, it receives the highest ratings from artists every year.", genre="rock", paid_on_spot = 1, date_start="2020-12-07",date_end="2020-12-08",location="Trenčín",price="80",max_capacity="100000",remaining_capacity="100000")
    db.session.add(f_pohoda)
    f_grape = Festival(name="Grape", description="Open-air summer music festival, first organized in 2010",genre="pop", paid_on_spot = 0, date_start="2020-08-13",date_end="2020-08-14",location="Piešťany Airport", price="60",max_capacity="70000",remaining_capacity="70000")
    db.session.add(f_grape)
    
    db.session.commit()
    #----------

    #STAGES
    s_Pohoda = Stage(name="Orange stage", festival=f_pohoda, create_schedules=[f_pohoda.date_start, f_pohoda.date_end])
    db.session.add(s_Pohoda)
    s_Urpiner = Stage(name="Urpiner stage", festival=f_pohoda, create_schedules=[f_pohoda.date_start, f_pohoda.date_end])
    db.session.add(s_Urpiner)
    s_Budis = Stage(name="Budis stage", festival=f_pohoda, create_schedules=[f_pohoda.date_start, f_pohoda.date_end])
    db.session.add(s_Budis)

    s_grape = Stage(name="Grape Stage", festival=f_grape, create_schedules=[f_grape.date_start, f_grape.date_end])
    db.session.add(s_grape)
    s_suzuki = Stage(name="Suzuki Stage", festival=f_grape, create_schedules=[f_grape.date_start, f_grape.date_end])
    db.session.add(s_suzuki)
    s_orange = Stage(name="Orange Stage", festival=f_grape, create_schedules=[f_grape.date_start, f_grape.date_end])
    db.session.add(s_orange)
    db.session.commit()
    #----------
    
    #-----INTERPRETS-----

    #POHODA STAGE
    i_Ware = Interpret(name="Jessie Ware",members="Jessie Ware",rating="8",genre="r&b and soul")
    db.session.add(i_Ware)
    i_Fink = Interpret(name="Fink",members="Fink",rating="9",genre="blues")
    db.session.add(i_Fink)
    i_Calexico = Interpret(name="Calexico",members="Joey Burns, John Convertino, Scott Colberg, Martin Wenk", rating = "7", genre="country")
    db.session.add(i_Calexico)
    #URPINER
    i_Dragon = Interpret(name="Little Dragon", members="Yukimi Nagano, Fredrik Wallin, Hakan Wirenstrand, Erik Bodin", rating = "6", genre="electro")
    db.session.add(i_Dragon)
    i_Blossoms = Interpret(name="Blossoms", members="Tom Ogden, Charlie Salt, Josh Dewhurst, Joe Donovan, Myles Kellock", rating = "8", genre="pop")
    db.session.add(i_Blossoms)
    i_GlassAnimals = Interpret(name="Glass Animals", members="Dave Bayley, Drew MacFarlane, Ed Irwin, Joe Seaward", rating = "9", genre="electro")
    db.session.add(i_GlassAnimals)   
    #BUDIS
    i_Longital = Interpret(name="Longital", members="Daniel Salontay, Jana Lokšenincová", rating = "5", genre="blues")
    db.session.add(i_Longital)
    i_Knower = Interpret(name="Knower", members="Genevieve Artadi, Louis Cole", rating = "7", genre="jazz")
    db.session.add(i_Knower)
    i_GusGus = Interpret(name="GusGus", members="Daniel Agust Haraldsson, Magnus Jonsson, Hogni Egilsson", rating="8", genre="electro")
    db.session.add(i_GusGus)

    # Grape stage
    i_foster = Interpret(name="Foster the People", members="Mark Foster, Sean Cimino, Isom Innis, Mark Pontius", rating="6", genre="pop")
    db.session.add(i_foster)
    i_foals = Interpret(name="Foals", members="Yannis Philippakis, Jack Bevan, Jimmy Smith, Edwin Congreave", rating="7", genre="rock")
    db.session.add(i_foals)
    i_woodkid = Interpret(name="Woodkid", members="Yoann Lemoine", rating="9", genre="folk")
    db.session.add(i_woodkid)

    # Suzuki Stage
    i_kiasmos = Interpret(name="Kiasmos DJ set", members="Olafur Arnalds, Janus Rasmussem", rating="5", genre="dubstep")
    db.session.add(i_kiasmos)
    i_ghostpoet = Interpret(name="Ghostpoet", members="Obaro Ejimiwe", rating="8", genre="electro")
    db.session.add(i_ghostpoet)
    i_yunglean = Interpret(name="Yung Lean", members="Jonatan Leandoer Hastad", rating="6", genre="rap")
    db.session.add(i_yunglean)

    # Orange Stage
    i_french = Interpret(name="French 79", members="Simon Henner", rating="5", genre="electro")
    db.session.add(i_french)
    i_shura = Interpret(name="Shura", members="Alexandra Lilah Denton", rating="3", genre="pop")
    db.session.add(i_shura)
    i_boypablo = Interpret(name="Boy Pablo", members="Alexandra Lilah Denton", rating="8", genre="rock")
    db.session.add(i_boypablo)
    
    db.session.commit()
    #---------- 
        
    #APPENDING INTERPRETS TO STAGES
    s_Pohoda.performers.append(i_Ware)
    s_Pohoda.performers.append(i_Fink)
    s_Pohoda.performers.append(i_Calexico)    

    s_Urpiner.performers.append(i_Dragon)
    s_Urpiner.performers.append(i_Blossoms)
    s_Urpiner.performers.append(i_GlassAnimals)

    s_Budis.performers.append(i_Longital)
    s_Budis.performers.append(i_Knower)
    s_Budis.performers.append(i_GusGus)

    s_grape.performers.append(i_foster)
    s_grape.performers.append(i_foals)
    s_grape.performers.append(i_woodkid)

    s_suzuki.performers.append(i_kiasmos)
    s_suzuki.performers.append(i_ghostpoet)
    s_suzuki.performers.append(i_yunglean)

    s_orange.performers.append(i_french)
    s_orange.performers.append(i_shura)
    s_orange.performers.append(i_boypablo)

    db.session.commit()
    #----------

    # Schedules
    pohoda_p1 = Performance(start="16:00",end="20:00",interpret = i_Ware, schedule = s_Pohoda.schedules[0] )
    db.session.add(pohoda_p1)
    pohoda_p2 = Performance(start="22:00", end="23:00", interpret = i_Fink,schedule = s_Pohoda.schedules[0])
    db.session.add(pohoda_p2)
    pohoda_p3 = Performance(start="17:00", end="19:00", interpret = i_Fink, schedule = s_Pohoda.schedules[1])
    db.session.add(pohoda_p3)
    pohoda_p4 = Performance(start="20:00", end="22:00", interpret = i_Calexico, schedule = s_Pohoda.schedules[1])
    db.session.add(pohoda_p4)

    pohoda_p5 = Performance(start="14:00", end="17:00", interpret = i_Dragon, schedule = s_Urpiner.schedules[0])
    db.session.add(pohoda_p5)
    pohoda_p6 = Performance(start="17:00", end="20:00", interpret = i_Blossoms, schedule = s_Urpiner.schedules[0])
    db.session.add(pohoda_p6)
    pohoda_p7 = Performance(start="16:00", end="19:00", interpret = i_Blossoms, schedule = s_Urpiner.schedules[1])
    db.session.add(pohoda_p7)
    pohoda_p8 = Performance(start="20:00", end="22:00", interpret = i_GlassAnimals, schedule = s_Urpiner.schedules[1])
    db.session.add(pohoda_p8)
    
    pohoda_p9 = Performance(start="15:00", end="17:00", interpret = i_Longital, schedule = s_Budis.schedules[0])
    db.session.add(pohoda_p9)
    pohoda_p10 = Performance(start="18:00", end="21:00", interpret = i_Knower, schedule = s_Budis.schedules[0])
    db.session.add(pohoda_p10)
    pohoda_p11 = Performance(start="16:00", end="20:00", interpret = i_Knower, schedule = s_Budis.schedules[1])
    db.session.add(pohoda_p11)
    pohoda_p12 = Performance(start="21:00", end="23:00", interpret = i_GusGus, schedule = s_Budis.schedules[1])
    db.session.add(pohoda_p12)

    grape_p1 = Performance(start="17:00", end="18:00", interpret=i_foster, schedule=s_grape.schedules[0])
    db.session.add(grape_p1)
    grape_p2 = Performance(start="20:00", end="21:30", interpret=i_woodkid, schedule=s_grape.schedules[0])
    db.session.add(grape_p2)
    grape_p3 = Performance(start="20:00", end="21:30", interpret=i_foals, schedule=s_grape.schedules[1])
    db.session.add(grape_p3)
    grape_p4 = Performance(start="22:00", end="23:00", interpret=i_woodkid, schedule=s_grape.schedules[1])
    db.session.add(grape_p4)

    grape_p5 = Performance(start="19:00", end="20:00", interpret=i_kiasmos, schedule=s_suzuki.schedules[0])
    db.session.add(grape_p5)
    grape_p6 = Performance(start="21:00", end="23:30", interpret=i_yunglean, schedule=s_suzuki.schedules[0])
    db.session.add(grape_p6)
    grape_p7 = Performance(start="20:00", end="21:30", interpret=i_ghostpoet, schedule=s_suzuki.schedules[1])
    db.session.add(grape_p7)
    grape_p8 = Performance(start="22:00", end="23:00", interpret=i_kiasmos, schedule=s_suzuki.schedules[1])
    db.session.add(grape_p8)

    grape_p9 = Performance(start="17:00", end="18:00", interpret=i_shura, schedule=s_orange.schedules[0])
    db.session.add(grape_p9)
    grape_p10 = Performance(start="20:00", end="21:30", interpret=i_french, schedule=s_orange.schedules[0])
    db.session.add(grape_p10)
    grape_p11 = Performance(start="19:00", end="20:30", interpret=i_french, schedule=s_orange.schedules[1])
    db.session.add(grape_p11)
    grape_p12 = Performance(start="22:30", end="23:30", interpret=i_boypablo, schedule=s_orange.schedules[1])
    db.session.add(grape_p12)
    
    db.session.commit()
    #-----------
        

   
    #s_Levy = Stage(name="Levy_stage", festival=f_grape, create_schedules=[f_grape.date_start, f_grape.date_end])
    #db.session.add(s_Levy)
    #eminem = Interpret(name="Eminem",members="Eminem",rating="10",genre="rap")
    #db.session.add(eminem)
    #abusus = Interpret(name="Abusus",members="Branko Jóbus",rating="10",genre="folk")
    #db.session.add(abusus)
    #elan = Interpret(name="Elán",members="Jožko Vajda",rating="6",genre="pop")
    #db.session.add(elan)
    #nohavica = Interpret(name="Jaromír Nohavica",members="Jaromír Nohavica",rating="10",genre="folk")
    #db.session.add(nohavica)
    #db.session.commit()
    #s_O2.performers.append(eminem)
    #s_O2.performers.append(elan)
    #s_Levy.performers.append(nohavica)
    #s_Levy.performers.append(elan)
    #s_Orange.performers.append(nohavica)
    #s_Orange.performers.append(abusus)
    #db.session.commit()
