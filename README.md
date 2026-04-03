# Voynich Solving

> Un proyecto computacional para comprobar si la seccion de recetas del Manuscrito Voynich se parece a una base de datos farmaceutica medieval.

**Autor:** Ntizar  
**Estado:** investigacion completada, linea semantica no resuelta  
**Sesiones:** 17

## La idea, en claro

La propuesta de este proyecto nunca fue solo "adivinar palabras" del Voynich.

La idea fuerte era otra: tratar la seccion de recetas no como prosa cifrada, sino como un sistema de notacion estructurado, parecido a una base de datos medieval de ingredientes y recetas.

Eso implicaba dos preguntas distintas:

1. **Pregunta estructural:** la seccion de recetas se comporta como una base de datos farmaceutica?
2. **Pregunta semantica:** podemos demostrar que un stem concreto del Voynich significa un ingrediente concreto?

La investigacion de estas semanas ha dejado claro que esas dos preguntas no tienen hoy la misma respuesta.

## Lo que si se sostiene

La parte mas fuerte del proyecto es la **estructura**.

La seccion de recetas del Voynich muestra varios rasgos anomalo-estables frente a controles medicos latinos:

- entropia de sufijos mucho mas baja de lo esperable
- alineacion vertical muy superior a la de textos en prosa
- variacion de esquema entre secciones compatible con escritura tabular o notacion funcional
- perfil estadistico que no encaja bien con un cifrado clasico

Resumen honesto y defendible:

> La seccion de recetas del Voynich parece una notacion estructurada compatible con una base de datos farmaceutica medieval.

Esa es, ahora mismo, la tesis fuerte del repositorio.

## Lo que no hemos conseguido demostrar

La parte debil sigue siendo la **lectura semantica**.

El proyecto genero hipotesis interesantes de tipo `stem -> ingrediente`, pero al endurecer la validacion aparecieron los limites:

- `v7` estaba contaminado por haber usado informacion de todos los folios, incluidos los de test
- varias metricas perfectas de `v7` eran tautologicas porque los targets se habian elegido por best-match
- `v8`, construido solo con train, captura algo de senal pero pierde contra baselines triviales en test ciego
- la cobertura directa del texto sigue siendo baja: alrededor del `18.7%`

En otras palabras: hay estructura real, pero no hemos podido convertirla en una lectura demostrada.

## La ultima ronda, a por todas

La sesion final intento exprimir la linea semantica con el criterio mas duro posible:

- benchmark comun sobre varias representaciones de entrada
  - `STA stems`
  - `STA tokens`
  - `EVA tokens`
- diagnostico del corpus de recetas historicas
- ampliacion del corpus con nuevas recetas priorizadas
- busqueda en fuentes abiertas externas
- incorporacion paralela de testigos de farmacopeas de Amsterdam
- nueva evaluacion ciega sobre corpus aumentado

El resultado fue util, pero no suficiente.

### Benchmark base

| Representacion | Fixed-F1 | Mejor baseline | Resultado |
|---|---:|---:|---|
| `sta_stem_frozen` | 41.0% | 64.8% | falla |
| `sta_token` | 47.6% | 73.5% | falla |
| `eva_token` | 42.9% | 67.8% | falla |

### Benchmark con corpus aumentado

| Representacion | Fixed-F1 | Mejor baseline | Resultado |
|---|---:|---:|---|
| `sta_stem_frozen` | 44.6% | 70.5% | falla |
| `sta_token` | 51.7% | 67.6% | falla |
| `eva_token` | 60.5% | 87.6% | falla |

La expansion externa movio algunas cifras, pero no produjo una victoria clara y reproducible sobre las baselines.

## Donde estamos ahora

La conclusion del proyecto no es "hemos resuelto el Voynich".

La conclusion seria y util es esta:

1. **La hipotesis estructural sigue viva y es defendible.**
2. **La hipotesis semantica sigue abierta, pero no demostrada.**
3. **No hay base honesta para vender desciframiento.**

Si este trabajo se presenta fuera del repositorio, la forma correcta de contarlo es:

> El Voynich, al menos en la seccion de recetas, muestra una estructura compatible con una base de datos farmaceutica medieval; las asignaciones concretas de stems a ingredientes siguen siendo hipotesis de trabajo.

## Proximos pasos realistas

Quedan dos caminos posibles.

### Camino 1: cerrar bien la linea semantica

Congelar el estado actual y dejar la parte de mapping como linea exploratoria no confirmada.

Esto tiene sentido si el objetivo es publicar o enseñar el proyecto con honestidad metodologica.

### Camino 2: ultima reanudacion futura, pero con regla dura

Solo reabrir la linea semantica si aparece una mejora que cumpla al menos estas condiciones:

- test ciego real
- ganancia clara frente a la mejor baseline
- repetibilidad
- baja contradiccion interna

Si eso no ocurre, lo correcto es mantener el proyecto como evidencia estructural, no como desciframiento.

## Como esta organizado el repo

- `Voynich_Solving/structural_analysis/`  
  La parte mas robusta y publicable.

- `Voynich_Solving/mapping_hypotheses/`  
  La parte exploratoria de `stem -> ingrediente`.

- `Voynich_Solving/docs/VALIDATION.md`  
  Validacion y limites reales del pipeline.

- `Voynich_Solving/docs/RECIPE_EXPANSION.md`  
  Como se intento ampliar el corpus sin hacer trampas.

- `Voynich_Solving/docs/SOURCE_NOTES_AMSTERDAM_1701.md`  
  Fuentes externas usadas en la ultima ronda.

## En una frase

Este proyecto no ha descifrado el Voynich, pero si ha reunido evidencia seria de que su seccion de recetas se parece mas a una notacion farmaceutica estructurada que a una prosa cifrada cualquiera.
