#### Theory of Relationship Bindings

##### The Problem

Say you have some object - Object A (O~A~) - and some object - Object B (O~B~). O~A~ has evidence that some object O~X~ could potentially exist where a concrete relationship O~A~ &#8594; O~X~ is established. From the perspective of O~A~, O~B~ (our evidence of the existence of O~X~) doesn't concretely exist. In the case where O~B~ does concretely exist, there must be some record of that; in that case this problem is null, because O~A~ can concretely confirm the existance of O~B~. In the case of relationships semantics, in all likelihood the existance of any relationship between any two nodes - not concretely known to eachother - likely share one of two types of fundemental relationships (i) a composite relationship, where O~A~ is composed in part or in whole by some proportion of O~B~ (composition) or (ii) where some O~B~ is a parent of the child O~A~ (inheritance). If the concept of semantic relationship theorems is not familiar I recommend this [read](https://medium.com/neo4j/graph-data-modeling-all-about-relationships-5060e46820ce). So then the most logical question to ask is, why does O~A~ have some confidence that O~X~ exists? To answer this we have to istantiate O~A~ as something more concrete. O~A~ is comprised of some data; at this point the type, volume, and format are all irrelevant. What does matter is that O~A~ has some finite set of properties (be it agnositically typed or formatted) which summaratively comprise O~A~.
<br />

Lets look at a mathematical example. Let some function:
$$f(x) = x^4 + 2x^3 + 6x^2 + 12x + 12$$
This function f(x) is comprised of 5 unique functions which change the behaviour of f(x) over some infinite domain. Truth is the "comparison" - and yes I am using that term loosely - is more complex in this case than it might seem on the surface, comparing f(x) to some arbituary function g(x) is actually quite abstract. So yes I will admit although it seems tempting to say so, this exercise will not solve our problem completely, you might even have a hard time linking it to our original problem - but thats not the purpose. Now that we have something more concrete what if we reframe our original question to something like why is f(x) related to g(x)? You might come up with several different answers like:

- Overall distance?
- Structural matching?
- Behavior at infinity?
- Graph shape?
- Derivative behavior?

This is confusing right? Because how f(x) actually relates to g(x) depends on the context of each function. For example, lets define some g(x) as:
$$g(x) = x^4 + 2x^3 + 5x^2 + 10x + 8$$
Now if we compare f(x) to g(x) as we see them on the page we might say: "Well the leading term is same (x^4^) ⇒ asymptotic behavior same, the lower degree coefficients are close but not identical ⇒ small deviation at moderate values of x. So g(x) must be comparitively alike f(x).". And to that I might agree. It does seem like f(x) is alike g(x). Now we actually know that these two function are alike in a couple of the ways we described above. But it doesn't hurt to wonder, if f(x) is like g(x) functionally - in the way we observed atleast - does that mean it behaves the similarly at infinity, does the graph shape visually look the same, is the derivative behaviour similar? Well I suppose what you can get out of this is, that relationships are complex... really complex. Any object can be related to any other object based on some undefined set of rules, parameters, and properties. There really is no one size fits all shoe for relationships. Wouldn't it be nice to just say O~A~ is related to O~B~ because I calculated it with {insert overly complex, hard to understand, lets admit completely bullshit formula}? Well let me answer that, yes it would be; but its not.
<br />
So now that we have taken that mathematical side track lets refocus on our original problem, but now we are going to spin it in a more specific (still not specific), more representative problem which actually faces the use case that is being investigated. Data Engineering. So I am going to specify some assumptions about O~A~ and O~B~ that aren't necessarily related to the problem, but more so allow me to represent it in a more digestable manor. Here are the two objects in question:

O~A~:
```json
{
    "company": "XMP"
    "employees": ["Parker", "Jason", "Emily"],
}
```
O~B~:
```json
{
    "name": "Parker",
    "age": "20"
}
```
Now can you tell me how these two entities are related? You probably though immediately "Parker that works for XMP.". All smug you are. Well what if I switch it up? That was too easy what if I change it so:
O~A~:
```json
{
    "a": "XMP"
    "b": ["Parker", "Jason", "Emily"],
}
```
O~B~:
```json
{
    "c": "Parker",
    "d": "20"
}
```
Now I know there will be people that say "Parker that works for XMP.". Yeah well done, you got the answer. But instead of just thinking you are all smart, lets think more constructively. Truth is you don't know now concretely how O~A~ is related to O~B~. And for reference sake a computer is not going to know any better, infact they will know worse. Now this isn't the whole problem but we will get to that. Essentially what I am demonstrating here is that even with the "obvious" in our hands the computer is not going to know any better on how O~A~ and O~B~ is related to one another. So lets tell it! I know I going to get shredded for this but sometimes the simplest answer is the best one. A computer cannot reason reliably without defined directives; O~A~ and O~B~ are just things, no different than they were at the start to us. We have to tell the computer our "knowledge" for it to decern how O~A~ is related to O~B~. One way to do this is describe the relationship as a form of an SPO (subject, predicate, object) triple which if you are unfamilar you can read up [here](https://en.wikipedia.org/wiki/Semantic_triple). As an example we could define a relationship some object type could have in terms of its SPO. At its most abstract state you could say:

TYPEX - IS_RELATED &#8594; TYPEY (Where TYPE is to designate that we are describing that the relationship exists between two types.)

Refining this more we could say:

```json
{
    "subject": {
        "type": "X",
        "sourceField": "X"
    },
    "predicate": {
        "value": "Y",
    },
    "object": {
        "type": "Z",
        "targetField": "Z"
    }
}
```
If then defined both of these in terms of O~A~ and O~B~. We get:
(i) Person - WORKS_FOR &#8594; Company
(ii)
```json
{
    "subject": {
        "type": "Person",
        "sourceField": "name"
    },
    "predicate": {
        "value": "WORKS_FOR",
    },
    "object": {
        "type": "Company",
        "targetField": "employees"
    }
}
```
This can become more or less generic, truly it is elastic based on use case. This expansion on the idea of SPO is where RDF (reasource description framework) comes from. And in essence what we just built in the most basic sense is an RDF.
