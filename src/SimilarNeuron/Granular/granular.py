from itertools import product
import gc, sys, os, json
from typing import Iterable, Iterator, Dict, Tuple, Union, Any, Set
from abc import ABCMeta, abstractmethod

mainfile = os.path.split(sys.argv[0])[0]

def structure(cls: "GranularMeta", json: bool = False) -> Dict[Union[str, "GranularMeta"], Iterable]:
    '''实体结构'''

    def method(self) -> Iterator:
        try:
            res = self.__subclasses__()
        except AttributeError:
            return self.iter
        if res:
            return res
        return self

    def _next(clssub: Iterable) -> Union[dict, list]:
        if isinstance(clssub, container):
            return list(clssub)
        return {i: _next(method(i)) for i in clssub}

    def _next_json(clssub: Iterable) -> Union[dict, list]:
        if isinstance(clssub, container):
            return list(clssub)
        return {str(i): _next_json(method(i)) for i in clssub}

    if hasattr(cls, "__subclasses__"):
        subclasses = cls.__subclasses__()
        if not subclasses:
            subclasses = list(cls)
    else:
        subclasses = cls.iter
    if not json:
        return {cls: _next(subclasses)}
    return {str(cls): _next_json(subclasses)}

def iterproduct(cls: "GranularMeta") -> list:
    granulariter = structure(cls)[cls]
    if len(granulariter) >= 1:
        return granulariter
    return []

class container(list):
    pass

class GranularMeta(ABCMeta):
    '''实体抽象元类'''

    def __iter__(cls):
        '''终端子域'''
        return (i for i in gc.get_objects() if isinstance(i, cls))
    
    def __hierarchy__(cls) -> Iterator:
        '''层次'''
        d = cls.structure()
        def putk(k: Iterable):
            res = []
            args = []
            for i in k:
                try:
                    res+=list(i.keys())
                    args+=list(i.values())
                except AttributeError:
                    res+=list(i)
            yield res
            if args:
                yield from putk(args)
        yield list(d.keys())
        yield from putk(list(d.values()))        

    def __relationship__(cls, typeset = False) -> Iterator[Union[Set, Tuple]]:
        '''关系'''
        if typeset:
            return list(map(set, product(*(i for i in cls.__subclasses__()))))
        return list(product(*(i for i in cls.__subclasses__())))
    
    def __relationship_map__(cls):
        '''关系映射'''
        return [list(product(*i)) for i in cls.__relationship__()]
    
    def __product__(cls):
        '''笛卡尔积'''
        return list(product(*cls.structure()[cls].keys()))

    def structure(cls, json: bool = False) -> Dict[Union[str, "GranularMeta"], Iterable]:
        '''实体结构'''
        def method(self) -> Iterator:
            try:
                res = self.__subclasses__()
            except AttributeError:
                return self.iter
            if res:
                return res
            return self

        def _next(clssub: Iterable) -> Union[dict, list]:
            if isinstance(clssub, container):
                return list(clssub)
            return {i: _next(method(i)) for i in clssub}

        def _next_json(clssub: Iterable) -> Union[dict, list]:
            if isinstance(clssub, container):
                return list(clssub)
            return {str(i): _next_json(method(i)) for i in clssub}

        if hasattr(cls, "__subclasses__"):
            subclasses = cls.__subclasses__()
            if not subclasses:
                subclasses = list(cls)
        else:
            subclasses = cls.iter
        if not json:
            return {cls: _next(subclasses)}
        return {str(cls): _next_json(subclasses)}

    def save_structure(cls, path: str = None):
        '''保存实体结构'''
        if not path:
            path = os.path.join(mainfile, "structure.json")
        with open(path, "w", encoding='utf-8') as f:
            f.write(json.dumps(cls.structure(json = True), ensure_ascii=False, indent=4))

class BaseSubstance(metaclass = GranularMeta):
    '''实体抽象基类'''

class Region(BaseSubstance):
    '''域'''

    @abstractmethod
    def add(self):
        ...

    @abstractmethod
    def remote(self):
        ...

    @abstractmethod
    def clear(self):
        ...

    def __iter__(self):
        return iter(self.iter)

class Ordinary(Region):
    '''通用域'''
    
    def __init__(self, name: str, subiter: Iterable[Any] = None) -> None:
        self.name = name
        if subiter:
            self.iter = container(subiter)
        else:
            self.iter = container()

    def add(self, *identification: Iterable[Any]) -> None:
        for i in identification:
            self.iter.append(i)

    def remote(self, *identification: Iterable[Any]) -> None:
        for i in identification:
            self.iter.remove(i)
    
    def clear(self) -> None:
        self.iter.clear()
    
    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return self.name

class BaseRelationship(BaseSubstance):
    '''关系基类'''
    ...
