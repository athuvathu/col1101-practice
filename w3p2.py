EPS = 1e-6

def is_equal(x, y):
    """Return True when x and y should be treated as equal."""
    return abs(x - y) <= EPS


def is_less(x, y):
    """Return True when x is definitely smaller than y."""
    return x < y - EPS

def is_greater(x, y):
    """Return True when x is definitely greater than y."""
    return x > y + EPS
    
def is_less_equal(x, y):
    """Return True when x should be treated as less than or equal to y."""
    return not is_greater(x, y)
    
def is_greater_equal(x, y):
    """Return True when x should be treated as greater than or equal to y."""
    return not is_less(x, y)
    
def square_sum(v):
    return ((v[0])**2 + (v[1])**2 + v[2]**2)
    
def mult(v, s):
    return (v[0]*s, v[1]*s, v[2]*s)
def vec_sum(v1, v2):
    return (v1[0]+v2[0], v1[1]+v2[1], v1[2]+v2[2])
    
def quad_solver(x, v, a, l, r):
    C = x
    B = v
    A = a/2
    
    if(is_equal(A, 0)):
        if(is_equal(B, 0)):
            if(is_equal(C, 0)): return -2
            return -1
        r1 = -C/B
        if(is_greater_equal(r1, l) and is_less_equal(r1, r)): return set([r1])
        return -1
    
    if(is_less(B**2 - 4*A*C, 0)): return -1
    r1 = (-B-(B**2 - 4*A*C)**(0.5))/(2*A)
    r2 = (-B+(B**2 - 4*A*C)**(0.5))/(2*A)
    
    res = []
    
    if(is_greater_equal(r1, l) and is_less_equal(r1, r)): res.append(r1)
    if(is_greater_equal(r2, l) and is_less_equal(r2, r)): res.append(r2)
    
    if(res): return set(res)

    return -1    
    
class Flight:
    """A single aircraft."""
    _accel = (0, 0, 0)
    _status = "does not exist"
    
    def __init__(self, max_speed, position, velocity, time=0):
        """
        max_speed : int, the highest speed this flight may hold
        position : a tuple (x, y, z) of integers, where it starts
        velocity : a tuple (vx, vy, vz) of integers, its initial velocity
        
        A newly created flight has the given initial velocity and acceleration
        (0, 0, 0). Its status must already be correct at the moment it is
        created.
        """
        self._working = True
        self._time = time
        
        self._max_speed = max_speed
        self._pos = position
        self._vel = velocity
        self._status = "flying"
        self.set_acceleration(time, (0, 0, 0))
        
    
    def _state(self, t):
        # returns pos and vel at time t
        t0 = self._time
        pos = vec_sum(vec_sum(self._pos, mult(self._vel, (t-t0))), mult(self._accel,((t-t0)**2)/2))
        vel = vec_sum(self._vel, mult(self._accel, (t-t0)))
        return (pos, vel)
        
    def _collision(self, f2, t):

        if((not self._working) or (not f2._working)):
            return False

        t0 = self._time
        ts = []
        #relative 
        for i in range(3):
            a = self._accel[i]-f2._accel[i]
            v = self._vel[i]-f2._vel[i]
            d = self._pos[i]-f2._pos[i]
            
            t1 = quad_solver(d, v, a, 0, t-t0)
            if(isinstance(t1, set)):
                ts.append(t1)
                continue
            if(is_equal(t1, -2)): continue
            if(is_equal(t1, -1)): return False
            
        if(not ts):
            self._retire()
            f2._retire()
            return True
            
        res = ts[0]
        for el in ts:
            res = res.intersection(el)
        res = list(res)
        if(not len(res)): return -1
            
        if(self._check_damage(res[0]+t0)): return False
        if(f2._check_damage(res[0]+t0)): return False
        self._retire()
        f2._retire()
        
        return True
    
    def __check_crash(self, t):
        t0 = self._time
        pz = self._pos[2]
        az = self._accel[2]
        vz = self._vel[2]
        
        fpz = self._state(t)[0][2]
        fvz = self._state(t)[1][2]
        if(is_less(fpz, 0)):
            return True
        if(is_less(pz, 0)):
            return True
        if(is_equal(fpz, 0) and is_less(fvz, 0)):
            return True

        if(az and is_greater_equal(fvz, 0) and is_less_equal(vz, 0)):
            # v = v0 + a(t-t0)
            # -v0/a + t0 = t
            t1 = (-vz)/az + t0
            if(is_less(self._state(t1)[0][2], 0)):
                return True
        
        return False
    
    def _retire(self):
        self._working = False
        self._status = "accident"
    
    def _check_damage(self, t):
        if(not self._working): return True
        _, new_vel = self._state(t)
        # velocity is updated linearly so its sufficient to check the end vel
        if(is_greater(square_sum(new_vel), self._max_speed**2) or self.__check_crash(t) or is_greater(square_sum(self._vel), self._max_speed**2)):
            self._retire()
            return True
        return False
        
    def _update(self, t):
        if(not self._working): return
        if(self._check_damage(t)): return
        
        self._pos, self._vel = self._state(t)
        self._time = t
        
    def _check_landed(self):
        if(not is_equal(self._pos[2], 0)): return
        if(not is_equal(square_sum(self._vel), 0)): return
        if(not is_equal(square_sum(self._accel), 0)): return

        self._status = "landed safely"
        self._working = False

    def set_acceleration(self, time, acceleration):
        """
        time : the instant from which the new acceleration applies
        acceleration : a tuple (ax, ay, az) of integers
        
        A flight that has already finished ignores this instruction.
        """
        if(not self._working): return
        self._update(time)
        self._accel = acceleration
        self._check_landed()
        
    def status(self, time):
        """
        Return this flight’s status at the given instant: "flying",
        "accident" or "landed safely".
        """
        if(not self._working): return self._status
        self._update(time)
        return self._status


class AirTrafficControl:
    """The controller, which owns every flight."""

    def __init__(self):
        """Start a new session, with no flights, at time 0."""
        self._t = 0
        self._flights = dict()
        self._keys = []
        
    def _update(self, t):
        n = len(self._keys)
        for i in range(n):
            for j in range(i+1, n):
                k1 = self._keys[i]
                k2 = self._keys[j]
                f1 = self._flights[k1]
                f2 = self._flights[k2]
                
                f1._collision(f2, t)
        for k in self._keys:
            self._flights[k]._update(t)

    def create(self, time, flight_id, max_speed, position, velocity):
        """Create a flight with the given position and initial velocity."""
        f = Flight(max_speed, position, velocity, time)
        self._keys.append(flight_id)
        self._flights[flight_id] = f
        self._update(time)

    def update(self, time, flight_id, acceleration):
        """Send an acceleration instruction to a flight at the given instant."""
        self._update(time)
        self._flights[flight_id].set_acceleration(time, acceleration)

    def status(self, time, flight_id):
        """
        Return the status of the given flight at the given instant: "flying",
        "accident", "landed safely", or "does not exist" if no flight with
        that identifier has ever been created.
        """
        self._update(time)
        if(flight_id not in self._flights): return "does not exist"
        return self._flights[flight_id].status(time)


    
atc = AirTrafficControl()

# CREATE 0 SG55 3 0 0 10 0 0 0
atc.create(0, "SG55", 3, (0, 0, 10), (0, 0, 0))

# UPDATE 0 SG55 2 0 0
atc.update(0, "SG55", (2, 0, 0))

# CREATE 0 SG56 99 8 0 10 0 0 0
atc.create(0, "SG56", 99, (8, 0, 10), (0, 0, 0))

# UPDATE 0 SG56 -2 0 0
atc.update(0, "SG56", (-2, 0, 0))

# STATUS 1 SG55
print(atc.status(1, "SG55"))

# STATUS 2 SG55
print(atc.status(2, "SG55"))

# STATUS 2 SG56
print(atc.status(2, "SG56"))

# STATUS 3 SG56
print(atc.status(3, "SG56"))