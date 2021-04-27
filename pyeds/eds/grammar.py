#  Created by Martin Strohalm, Thermo Fisher Scientific
#  Adapted from Peter Norvig courses.

# import modules
import re


class Grammar(object):
    """
    Grammar class holds definition of a syntax grammar and provides a method to
    parse given text according to it.
    """
    
    
    def __init__(self, rules={}, whitespace="\s*", **kw_rules):
        """
        Initializes a new instance of Grammar.
        
        Each grammar rule consists of its unique name and expression. An
        expression can consists of one or more alternatives separated by ' | '.
        Each alternative then consists of one or more elements separated by
        space, where element can be either name of any other rule or a regular
        expression.
        
        Args:
            rules: dict
                Dictionary of grammar rules.
            
            whitespace: str
                Whitespace definition. If set to None, spaces between tokens
                will not be allowed.
            
            **kw_rules: key:value pairs
                Individual rules specified as key:value pairs.
        """
        
        # init rules
        self._rules = {}
        rules = list(rules.items()) + list(kw_rules.items())
        
        # set rules
        for key, value in rules:
            alts = str.split(value, ' | ')
            self._rules[key] = tuple(map(str.split, alts))
        
        # ensure whitespace set
        if "whitespace" not in self._rules:
            self._rules["whitespace"] = whitespace if whitespace is not None else ''
    
    
    def __str__(self):
        """Gets standard string representation."""
        
        return "\n".join("%s: %s" % (k, v) for k, v in self._rules.items())
    
    
    def __repr__(self):
        """Gets debug string representation."""
        
        return "%s(%s)" % (self.__class__.__name__, self.__str__())
    
    
    def parse(self, text, rule):
        """
        Parses given text into an expression tree according to specific top rule.
        
        Args:
            text: str
                Text to be parsed.
            
            rule: str
                Name of the rule to be applied at first. Typically this is the
                most parent rule combining all the detailed rules. The rule must
                exists inside grammar.
        
        Returns:
            hierarchical list
                Parsed text as hierarchical list of matches. Returns None if any
                part of the text cannot be parsed.
        """
        
        parsed = []
        
        # check rule
        if rule not in self._rules:
            message = "Unknown rule specified! --> '%s'" % rule
            raise KeyError(message)
        
        # parse text
        while text:
            
            result = self._parse(text, rule)
            if result is None:
                return None
            
            parsed.append(result[0])
            text = result[1]
        
        # return parsed tree
        return parsed
    
    
    @staticmethod
    def visualize(tree, bullet="    ", indent=""):
        """
        Visualize parsed tree.
        
        Args:
            tree: list
                Tree to visualize.
            
            bullet: str
                Character(s) used as visualization bullet.
            
            indent: str
                Character(s) used to indent current level.
        
        Returns:
            str
                Tree formatted for better readability.
        """
        
        # check tree
        if tree is None:
            return
        
        # print simple items directly
        if all(isinstance(x, str) for x in tree):
            return "%s%s,\n" % (indent, tree)
        
        # init buffer
        buff = ""
        
        # print rule name
        if isinstance(tree[0], str):
            buff += "%s['%s',\n" % (indent, tree[0])
            tree = tree[1:]
        else:
            buff += "%s[\n" % indent
        
        # increase indentation
        new_indent = indent + bullet
        
        # print matches
        for item in tree:
            
            # print matched text
            if isinstance(item, str):
                buff += "%s'%s',\n" % (new_indent, item)
            
            # print subtree
            else:
                buff += Grammar.visualize(item, bullet, new_indent)
        
        buff += "%s],\n" % indent
        
        return buff
    
    
    @staticmethod
    def extract(tree, rule):
        """
        Extracts values for given rule.
        
        Args:
            tree: hierarchical list
                Parsed text as hierarchical list of matches.
            
            rule: str
                Rule name to be extracted.
        
        Returns:
            hierarchical list
                List of rule values.
        """
        
        values = []
        
        # check tree
        if not tree:
            return values
        
        # search tree
        for item in tree:
            
            name = item[0]
            value = item[1:]
            
            # matching rule
            if name == rule:
                values.append(value)
            
            # go further
            else:
                values += Grammar.extract(value, rule)
        
        return values
    
    
    def _parse(self, text, rule):
        """Parses text using given rule."""
        
        # match rule to text
        if rule in self._rules:
            
            # try all rule alternatives
            for alt in self._rules[rule]:
                tree = []
                remainder = text
                
                # match each rule element
                for elm in alt:
                    result = self._parse(remainder, elm)
                    if result is None:
                        tree = None
                        break
                    
                    tree.append(result[0])
                    remainder = result[1]
                
                # return matched tree and remainder
                if tree is not None:
                    return [rule]+tree, remainder 
            
            return None
        
        # match pattern to text
        tokenizer = self._rules["whitespace"] + "(%s)"
        match = re.match(tokenizer % rule, text)
        if not match:
            return None
        
        # return matched part and remainder
        return match.group(1), text[match.end():]
