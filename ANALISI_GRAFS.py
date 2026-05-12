from graph_tool.all import Graph, VertexPropertyMap, Vertex, graph_draw, load_graph, label_components, pagerank, closeness, shortest_distance, betweenness, sfdp_layout
import matplotlib
matplotlib.use("Agg") #per poder guardar els histogrames en format png
import matplotlib.pyplot as plt
import math
import click

def get_histogram(data:list[int|float], titol:str, xlabel:str,ylabel:str, nom_fitxer:str)-> None:
    """Genera un histograma a partir de les dades proporcionades"""

    plt.figure()
    plt.hist(data, edgecolor='black')
    plt.title(titol)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(axis='y', linestyle='-', alpha=0.5)
    plt.tight_layout()
    plt.savefig(nom_fitxer)
    print(f"Histograma guardat com a {nom_fitxer}")


def get_graph(graph: Graph, data_to_vertex: VertexPropertyMap, data:list[int|float], legend_name:str, 
              graph_title:str, graph_name:str,indefinite_data:list[Vertex] | None = None)-> None:
    """Genera un graf a partir de les dades proporcionades"""

    color_property = graph.new_vertex_property("vector<float>")
    colors = plt.colormaps.get_cmap("hot")
    max_value = max(data)

    for vertex in graph.vertices():
        if indefinite_data is not None or max_value == 0:
            if max_value == 0 or vertex in indefinite_data:
                normalized = 0
                rgb_color = colors(normalized)[:3]
            else:
                normalized = data_to_vertex[vertex] / max_value  #normalitzem els valors
                rgb_color = colors(normalized)[:3]
            color_property[vertex] = list(map(float, rgb_color))
        else:
            normalized = data_to_vertex[vertex] / max_value  #normalitzem els valors
            rgb_color = colors(normalized)[:3]
            color_property[vertex] = list(map(float, rgb_color))


    figure, graph_axis = plt.subplots(figsize=(8, 8))
    graph_axis.set_title(graph_title)
    graph_axis.axis("off") 


    pos = sfdp_layout(graph)
    graph_draw( 
        graph,
        pos = pos,
        vertex_fill_color=color_property,
        bg_color=[1, 1, 1, 1], #fons blanc
        mplfig=graph_axis #llegenda
    )

    legend_axis = figure.add_axes([0.9, 0.25, 0.02, 0.5])  #posició llegenda
    norm = plt.Normalize(vmin=min(data), vmax=max_value) #dades llegenda
    color_map = plt.cm.ScalarMappable(norm=norm, cmap=colors)
    color_map.set_array([])
    legend_colors = figure.colorbar(color_map, cax=legend_axis, label = legend_name)

    plt.savefig(graph_name)
    print(f"Graf amb les dades obtingudes guardat com a {graph_name}")


def comunitats(graph:Graph)->None:
    '''
    Escriu el nº de comunitats que hi ha, el tamany d'aquestes i els usuaris que la formen
    També, genera un graf amb les diferents comunitats marcades
    '''
    components, hist = label_components(graph)
    handle_property = graph.vertex_properties["handle"]

    communities = {} #dict[num comunitat, usuaris que la formen]
    for vertex in graph.vertices():
        component_vertex = components[vertex]
        if component_vertex not in communities:
            communities[component_vertex] = [vertex]
        else:
            communities[component_vertex].append(vertex)

    print(f"Nombre de comunitats: {len(hist)}")
    for i in range(len(hist)):
        community_users = communities[i]
        community_handles = [handle_property[vertex] for vertex in community_users]
        print(f'Comunitat {i+1}: {hist[i]} usuaris ({', '.join(community_handles)})')

    #GRAF
    color_property = graph.new_vertex_property("vector<float>")
    colors1 = plt.colormaps.get_cmap("tab20") #fins la comunitat 20
    colors2 = plt.colormaps.get_cmap("Set3") #les comunitats restants

    for vertex in graph.vertices():
        community_index = components[vertex]
        if community_index < 20:
            rgb_color = colors1(components[vertex])[:3]
        else:
            rgb_color = colors2(components[vertex])[:3]
        color_property[vertex] = list(map(float,rgb_color))
        
    graph_draw(
        graph,
        vertex_fill_color=color_property,
        vertex_size=20,
        bg_color=[1,1,1,1], #fons blanc
        output="graph_comunitats.svg"
    )
    print()
    print("Graf amb les dades obtingudes guardat com a graph_comunitats.svg")


def reputacio(graph:Graph)->None:
    '''
    Escriu ordenadament la reputació que tenen els seguidors entre ells i genera un historgrama amb aquestes dades
    També, genera un graf de calor, com més groc / blanc sigui el vertex, més reputació té
    '''
    Pagerank = pagerank(graph)
    vertex_sorted = sorted(graph.vertices(), key= lambda x: -Pagerank[x]) #ordena els vertexs segons la seva reputació
    for vertex in vertex_sorted:
        print(f"{graph.vertex_properties["handle"][vertex]} -> {Pagerank[vertex]:.6f}")
    
    reputations = [Pagerank[vertex] for vertex in graph.vertices()] #llista amb tots els valors de les reputacions
    
    #HISTOGRAMA
    print()
    get_histogram(reputations,"Histograma de Reputació","Valor de reputació", 
                       "Nombre de vertexs (usuaris)", "histograma_reputacio.png")

    #GRAF
    get_graph(graph, Pagerank, reputations, "Reputació","Graf segons la reputació del seguidors", 
              "graph_reputacio.svg")

def usuaris_competidors(graph:Graph)-> None:
    '''
    Escriu ordenadament la competitivitat que tenen els seguidors entre ells. Com més aprop de l'1 estigui 
    la seva closeness més competitiu és. També, genera un histograma ammb aquestes dades i un graf de calor, 
    com més groc / blanc sigui el vertex, més competivitat té
    '''
    handle_property = graph.vertex_properties["handle"]
    closeness_values = closeness(graph)
    closeness_defined = [vertex for vertex in graph.vertices() if not math.isnan(closeness_values[vertex])] #vèrtexs amb competitivitat entre 0 i 1
    closeness_indefinite = [vertex for vertex in graph.vertices() if math.isnan(closeness_values[vertex])] #vèrtexs disjunts (competivitat Nan -> 0)
    closeness_sorted = sorted(closeness_defined, key=lambda v: -closeness_values[v])

    print("Ranking usuaris amb closeness més alta (potencials competidors):")
    for vertex in closeness_sorted:
        print(f"{handle_property[vertex]} - closeness: {closeness_values[vertex]:.4f}")
    
    print()
    print("Usuaris disjunts als altres (sense potencial competidor):")
    for vertex in closeness_indefinite:
        print(f"{handle_property[vertex]} - closeness: 0 (no connectat)")
        
    values_closeness = [closeness_values[vertex] for vertex in closeness_defined] + [0 for _ in closeness_indefinite] #sense els vèrtexs amb competivitat Nan - 0
    
    #HISTOGRAMA
    print()
    get_histogram(values_closeness,"Histograma de competitivitat","Valor de competitivitat", 
                       "Nombre de vertexs (usuaris)","histograma_competitivitat.png")

    #GRAF
    get_graph(graph,closeness_values,values_closeness,"Closenness", "Graf segons la competitivitat dels seguidros",
              "graph_usuaris_competidors.svg",closeness_indefinite)


def distancia_propagacio(graph:Graph) -> None:
    """
    Escriu ordenadament la màxima distància que pot assolir cada vèrtex (usuari) cap a altres usuaris.
    També, genera un histograma ammb aquestes dades i un graf de calor, com més groc / blanc sigui el 
    vertex, major és la seva distància de propagació
    """ 
    handle_property = graph.vertex_properties["handle"]
    distances_handles = {}
    distances_vertex = {}
    histogram_values = []
    distance_zero = []

    for vertex in graph.vertices():
        distances = shortest_distance(graph, source=vertex)
        max_dist = -1

        for dist in distances:
            if dist != 2147483647: #distanica infinita
                max_dist = max(dist,max_dist)
        
        distances_handles[handle_property[vertex]] = max_dist
        distances_vertex[vertex] = max_dist
        if max_dist != -1:
            histogram_values.append(max_dist)
        else:
            distance_zero.append(vertex)


    print("Ranking usuaris segons la distància de propagació:")
    for handle, dist_max in sorted(distances_handles.items(), key=lambda x: -x[1]):
        if dist_max == -1:
            print(f"{handle} - distància màxima: infinita (vèrtex disjunt)")
        else:
            print(f"{handle} - distància màxima: {dist_max}")
        
    #HISTOGRAMA 
    print()
    get_histogram(histogram_values,"Histograma de la distanica de propagació","Distànicia màxima",
                        "Nombre de vertexs (usuaris)","histograma_distancia_propagacio.png")

    #GRAF
    get_graph(graph,distances_vertex,histogram_values,"Distància propagació","Graf segons la distància de propagació", 
              "graph_distancia_propagacio.svg",distance_zero)
   

def vertexs_sortida(graph:Graph, client:str)->None:
    """
    Escriu els vèrtex que actuen com a sortides, és a dir, si ha respòs un post del client i un altre 
    usuari, que no ha contestat a cap post del client, l'ha contestat a ell. També, genera un histograma 
    amb aquestes dades i un graf de si actua o no com a sortida
    """
    handle_property = graph.vertex_properties["handle"]

    for vertex in graph.vertices():
        if handle_property[vertex] == client:
            vertex_client = vertex
            break
    
    commentators = set(vertex for vertex in graph.iter_out_neighbors(vertex_client)) #Usuaris que han comentat algun post del client

    usuaris_sortida = []
    for commentator in commentators:
        for veí in graph.iter_out_neighbors(commentator): #usuaris que han comentat algun comentari dels commentators
            if veí != vertex_client and veí not in commentators:
                usuaris_sortida.append(commentator)
                break  #amb 1 usuari que no sigui el client ni cap commentators, ja es sortida

    if usuaris_sortida:
        print("Usuaris que actuen com a vertexs de sortida cap a nous públics:")
        for vertex in usuaris_sortida:
            print(f"{handle_property[vertex]}")
    else:
        print("Tots els usuaris han respòs a algun post del client")

    num_vertex_sortida = len(usuaris_sortida)
    num_vertex_no_sortida = len(commentators)- num_vertex_sortida

    #HISTOGRAMA
    plt.figure()
    plt.bar(['Sí', 'No'], [num_vertex_sortida, num_vertex_no_sortida], color=['blue', 'red'])
    plt.title(f"Usuaris que actuen com a portes de sortida (Client: {client})")
    plt.ylabel("Nombre d'usuaris")
    plt.xlabel("És vèrtex sortida?")
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig("histograma_vertexs_sortida.png")
    print()
    print("Histograma amb les dades obtingudes guardat com a histograma_vertexs_sortida.png")

    #GRAF
    color_property = graph.new_vertex_property("vector<float>")
    color_si = [0, 0, 1]  #blau
    color_no = [1, 0, 0]  #vermell
    color_CLIENT = [0.8, 0.8, 0.8] 

    for vertex in graph.vertices():
        if vertex in usuaris_sortida:
            color_property[vertex] = color_si
        elif vertex in commentators:
            color_property[vertex] = color_no
        else:
            color_property[vertex] = color_CLIENT

    figure, graph_axis = plt.subplots(figsize=(10, 10))
    graph_axis.set_title(f"Gràfic de vertexs sortida (Client: {client})")
    graph_axis.axis("off")

    pos = sfdp_layout(graph)
    graph_draw(
        graph,
        pos=pos,
        vertex_fill_color=color_property,
        vertex_shape="circle",
        bg_color=[1, 1, 1, 1],
        mplfig= graph_axis #llegenda
    )

    #llegenda
    graph_axis.plot([], [], 'o', color=color_si, label='Comentador sortida')
    graph_axis.plot([], [], 'o', color=color_no, label='Comentador no sortida')
    graph_axis.plot([], [], 'o', color=color_CLIENT, label='Vertex client')

    graph_axis.legend(loc='best', bbox_to_anchor=(1, 0.5)) #posició llegenda

    plt.savefig("graph_vertexs_sortida.svg")
    print("Graf amb les dades obtingudes guardat com a graph_vertexs_sortida.svg")


def punts_pas(graph:Graph)->None:
    '''
    Escriu ordenadament els usuaris segons la seva influència com a punts de pas en entre els altres usuaris. 
    Com més alt és el valor d'un usuari, canalitza més punts de pas entre altres usuaris.
    També, genera un histograma ammb aquestes dades i un graf de calor, com més groc / blanc sigui el vertex,
    més punts de pas té
    '''
    handle_property = graph.vertex_properties["handle"]
    vertex_betweenness, edge_betweenness = betweenness(graph)
    betweenness_sorted = sorted(graph.vertices(), key=lambda v: -vertex_betweenness[v]) #ordena els vertexs segons la seva influènica com a punts de pas
    
    print("Ranking usuaris com a punts de pas:")
    for vertex in betweenness_sorted:
        print(f"{handle_property[vertex]} - betweenness: {vertex_betweenness[vertex]:.4f}")

    valors_betweenness = [vertex_betweenness[vertex] for vertex in graph.vertices()] #valors dels vèrtexs

    #HISTOGRAMA
    print()
    get_histogram(valors_betweenness,"Histograma de Betweenness","Betweenness", 
                       "Nombre de vertexs (usuaris)","histograma_punts_pas.png")

    #GRAF
    get_graph(graph, vertex_betweenness, valors_betweenness, "Punts pas", "Graf segons els punts de pas", 
              "graph_punts_pas.svg")


# Command line interface to test ANALISI_GRAFS operations ##################################################

@click.group()
def main():
    pass


@main.command("comunitats")
def cmd_comunitats():
    graph = load_graph("followers_graph.gt")
    comunitats(graph)


@main.command("reputacio")
def cmd_reputacio():
    graph = load_graph("followers_graph.gt")
    reputacio(graph)


@main.command("usuaris_competidors")
def cmd_usuaris_competidors():
    graph = load_graph("followers_graph.gt")
    usuaris_competidors(graph)


@main.command("distancia_propagacio")
def cmd_distancia_propagacio():
    graph = load_graph("graph_threads.gt")
    distancia_propagacio(graph)


@main.command("vertexs_sortida")
@click.argument("client")
def cmd_vertexs_sortida(client:str):
    graph = load_graph("graph_threads.gt")
    vertexs_sortida(graph,client)


@main.command("punts_pas")
def cmd_punts_pas():
    graph = load_graph("graph_threads.gt")
    punts_pas(graph)

if __name__ =='__main__':
    main()