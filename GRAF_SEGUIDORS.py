from graph_tool.all import Graph, graph_draw
from bsky import get_followers, get_relationships
import click


@click.command()
@click.argument("client")
def get_followers_graph(client:str)->None:
    '''Construeix un graf amb l’usuari, els seus seguidors i relacions entre ells.'''
    

    followers = get_followers(client) #Perfils dels seguidors
    followers_did = [follower.did for follower in followers] 
    did_to_handle = {follower.did: follower.handle for follower in followers}

    graph = Graph(directed=True)
    handle_property = graph.new_vertex_property("string") 
    graph.vertex_properties["handle"] = handle_property
    profile_property = graph.new_vertex_property("object")
    graph.vertex_properties["profile"] = profile_property
    handles_to_vertex = {} 
    
    #vèrtexs SEGUIDORS
    for follower in followers: 
        v_follower = graph.add_vertex()
        handle_property[v_follower] = follower.handle
        profile_property[v_follower] = follower
        handles_to_vertex[follower.handle] = v_follower


    #arestes entre SEGUIDORS
    for follower in followers:
        followers_did.remove(follower.did)
        relationships = get_relationships(follower.did, followers_did)
        
        #1. SEGUIDOR a SEGUIDORS
        for did in relationships.following:
            if did_to_handle.get(did) in handles_to_vertex:
                graph.add_edge(handles_to_vertex[follower.handle], handles_to_vertex[did_to_handle[did]])

        #2. SEGUIDORS a SEGUIDOR
        for did in relationships.followedBy:
            if did_to_handle.get(did) in handles_to_vertex:
                graph.add_edge(handles_to_vertex[did_to_handle[did]], handles_to_vertex[follower.handle])

    graph.save("followers_graph.gt")

    graph_draw(
        graph,
        vertex_shape="square", #vèrtexs quadrats
        vertex_size = 20,
        bg_color=[1,1,1,1], #fons blanc
        output="followers_graph.svg" 
        )

if __name__ == "__main__":
    get_followers_graph()


