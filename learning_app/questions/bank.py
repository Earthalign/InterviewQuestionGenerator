from __future__ import annotations

from learning_app.core.models import Question, QuestionKind
from learning_app.questions.shuffler import place_correct_answer_at


def _make_q(
    id: str,
    category: str,
    kind: QuestionKind,
    title: str,
    prompt: str,
    correct_answer: str,
    distractors: list[str],
    explanation: str,
    target_idx: int = 0,
) -> Question:
    """Tworzy pytanie z opcjami deterministycznie rozmieszczonymi na różnych pozycjach."""
    options = place_correct_answer_at(
        correct_answer=correct_answer,
        distractors=distractors,
        target_index=target_idx,
        seed=id,
    )
    return Question(
        id=id,
        category=category,
        kind=kind,
        title=title,
        prompt=prompt,
        options=options,
        correct_answer=correct_answer,
        explanation=explanation,
    )


def build_question_bank() -> list[Question]:
    """Zwraca bogatą, edukacyjną pulę pytań rekrutacyjnych dla Senior Python Developera."""
    return [
        # =====================================================================
        # 1. PYTHON — TEORIA
        # =====================================================================
        _make_q(
            id="py-mutable-default",
            category="Python",
            kind="theory",
            target_idx=1,  # B
            title="Modyfikowalny argument domyślny w funkcji",
            prompt=(
                "Dlaczego poniższa funkcja zachowuje stan z poprzednich wywołań?\n\n"
                "```python\n"
                "def dodaj(element, bufor=[]):\n"
                "    bufor.append(element)\n"
                "    return bufor\n"
                "```"
            ),
            correct_answer="Wartości domyślne argumentów są ewaluowane dokładnie raz w chwili definiowania funkcji (`def`), a modyfikowalny obiekt listy jest współdzielony pomiędzy wszystkimi kolejnymi wywołaniami.",
            distractors=[
                "W Pythonie listy przekazywane jako argumenty stają się automatycznie strukturami niemodyfikowalnymi (immutable) i tworzą nową instancję przy każdym wywołaniu.",
                "Zmienna `bufor` trafia automatycznie do zasięgu globalnego modułu z powodu użycia metody `append()`, co powoduje współdzielenie pamięci w procesie.",
                "Python ewaluuje argumenty domyślne na nowo po każdej instrukcji `return`, kopiując stan obiektu z poprzedniej ramki stosu wywołań.",
            ],
            explanation="W Pythonie wartości argumentów domyślnych są ewaluowane jednokrotnie, w chwili kompilacji instrukcji `def`, po czym trafiają do atrybutu `__defaults__` obiektu funkcji. Jeśli jako wartość domyślną przypiszemy modyfikowalny obiekt (taki jak lista czy słownik), każde kolejne wywołanie funkcji będzie modyfikować dokładnie tę samą instancję w pamięci. Z tego powodu powszechną i bezpieczną praktyką jest stosowanie `bufor=None` oraz tworzenie świeżej listy `bufor = []` w ciele funkcji. Pozwala to zagwarantować niezależność i izolację każdego wywołania.",
        ),
        _make_q(
            id="py-is-equals",
            category="Python",
            kind="theory",
            target_idx=2,  # C
            title="Tożsamość w pamięci a porównanie wartości (`is` vs `==`)",
            prompt="Jaka jest fundamentalna różnica pomiędzy operatorem `is` a operatorem `==` w języku Python?",
            correct_answer="`is` sprawdza tożsamość obiektów w pamięci (ten sam adres / `id`), natomiast `==` wywołuje metodę `__eq__` w celu porównania semantycznej równości wartości.",
            distractors=[
                "`is` porównuje zawartość struktur danych w pamięci, a `==` weryfikuje jedynie, czy zmienne należą do tej samej klasy bazowej.",
                "`is` służy wyłącznie do szybkiego porównywania łańcuchów znaków (str), podczas gdy `==` obsługuje typy numeryczne i kolekcje.",
                "Oba operatory działają identycznie, lecz `is` jest zoptymalizowaną składniowo wersją `==` wprowadzoną w Pythonie 3.10.",
            ],
            explanation="Operator `is` weryfikuje tożsamość referencji w pamięci i odpowiada sprawdzeniu `id(a) == id(b)`. Z kolei operator `==` deleguje porównanie do metody magicznej `__eq__`, co pozwala klasom definiować własną logikę równości wartości. Dwa odrębne obiekty o identycznej zawartości (np. dwie listy `[1, 2]`) będą równe dla `==`, lecz różne dla `is`. Z tego względu do porównywania singletonów języka, takich jak `None` czy `Ellipsis`, zawsze należy stosować `is None`.",
        ),
        _make_q(
            id="py-generators",
            category="Python",
            kind="theory",
            target_idx=3,  # D
            title="Generatory, protokół iteratora i zarządzanie pamięcią",
            prompt="Dlaczego generatory z instrukcją `yield` są preferowane do przetwarzania wielogigabajtowych strumieni danych?",
            correct_answer="Generują elementy leniwie (na żądanie), alokując w pamięci RAM wyłącznie bieżący element strumienia i zawieszając stan ramki funkcji pomiędzy krokami.",
            distractors=[
                "Automatycznie zrównoleglają przetwarzanie danych na wszystkie dostępne rdzenie procesora w wątkach CPythona.",
                "Gwarantują stałą złożoność czasową operacji O(1) dla dowolnego przekształcenia danych.",
                "Tworzą kopię strumienia danych w pamięci podręcznej L3 procesora, omijając magistralę systemową.",
            ],
            explanation="Generator implementuje metody protokołu iteratora: `__iter__` oraz `__next__`. Zamiast budować i alokować całą kolekcję w pamięci RAM naraz, funkcja generatora wstrzymuje wykonanie po napotkaniu `yield` i wznawia je dopiero przy kolejnym żądaniu wartości. Pozwala to na bezpieczne strumieniowanie plików przekraczających rozmiar dostępnej pamięci operacyjnej bez ryzyka błędu Out Of Memory. Dystraktory sugerujące automatyczne zrównoleglenie są błędne, ponieważ generator wykonuje się synchronicznie w pojedynczym wątku.",
        ),
        _make_q(
            id="py-decorators",
            category="Python",
            kind="theory",
            target_idx=0,  # A
            title="Metadane funkcji a dekorator `@functools.wraps`",
            prompt="Jaką rolę pełni dekorator `@functools.wraps` umieszczany na funkcji opakowującej (wrapperze) wewnątrz dekoratora?",
            correct_answer="Kopiuje metadane dekorowanej funkcji (m.in. `__name__`, `__doc__`, `__annotations__`) oraz ustawia atrybut `__wrapped__`, zapobiegając utracie tożsamości funkcji podczas introspekcji.",
            distractors=[
                "Automatycznie synchronizuje wywołania funkcji w środowisku wielowątkowym za pomocą systemowego mutexa.",
                "Przekształca funkcję synchroniczną w asynchroniczną coroutine kompatybilną z biblioteką `asyncio`.",
                "Wymusza uruchomienie udekorowanej funkcji w osobnym procesie roboczym z własną przestrzenią adresową.",
            ],
            explanation="Bez użycia `@functools.wraps` udekorowana funkcja traci swoją tożsamość i przejmuje nazwę oraz docstring funkcji wewnętrznej (zazwyczaj `wrapper`). Narzędzie to kopiuje atrybuty metadanych z oryginalnej funkcji do wrappera i tworzy dowiązanie `__wrapped__`. Jest to kluczowe dla poprawnego działania linterów, frameworków testowych oraz generatorów dokumentacji (np. OpenAPI w FastAPI lub Sphinx). Pominięcie tego dekoratora jest częstym błędem juniorów utrudniającym późniejszy debugging.",
        ),
        _make_q(
            id="py-gil",
            category="Python",
            kind="theory",
            target_idx=1,  # B
            title="Global Interpreter Lock (GIL) i model współbieżności w CPythonie",
            prompt="W jaki sposób Global Interpreter Lock (GIL) wpływa na programy wielowątkowe w standardowej implementacji CPython?",
            correct_answer="Zezwala tylko jednemu wątkowi na wykonywanie kodu bajtowego Pythona naraz w danym procesie; dla zadań obliczeniowych (CPU-bound) zaleca się osobne procesy (`multiprocessing`), podczas gdy dla I/O-bound wątki i `asyncio` działają efektywnie.",
            distractors=[
                "Gwarantuje automatyczne i równoległe rozłożenie wątków na wszystkie fizyczne rdzenie CPU dla operacji numerycznych.",
                "Blokuje wykonywanie asynchronicznych operacji sieciowych i wejścia/wyjścia (I/O-bound) w pętli zdarzeń.",
                "Zastępuje konieczność stosowania blokad `threading.Lock` w kodzie użytkownika, gwarantując thread-safety struktur danych.",
            ],
            explanation="GIL to mechanizm synchronizacji na poziomie interpretera CPython, który chroni zarządzanie pamięcią (przede wszystkim zliczanie referencji) przed współbieżnym uszkodzeniem. Z tego powodu operacje intensywne obliczeniowo (CPU-bound) nie zyskują na wielowątkowości w obrębie jednego procesu, a rozwiązaniem jest architektura wieloprocesowa (`multiprocessing`). Z kolei operacje wejścia/wyjścia (I/O) zwalniają GIL, dzięki czemu wątki i `asyncio` świetnie sprawdzają się przy komunikacji sieciowej. Należy pamiętać, że GIL nie chroni logiki biznesowej aplikacji — wyścigi na zmiennych współdzielonych nadal wymagają jawnych blokad `Lock`.",
        ),
        _make_q(
            id="py-async-blocking",
            category="Python",
            kind="theory",
            target_idx=2,  # C
            title="Blokowanie pętli zdarzeń w `asyncio`",
            prompt="Co się wydarzy, gdy funkcja asynchroniczna wykona długą operację synchroniczną (np. `time.sleep(5)`) w wątku pętli zdarzeń?",
            correct_answer="Główna pętla zdarzeń (`event loop`) zostanie całkowicie zamrożona, uniemożliwiając przełączanie kontekstu i obsługę jakichkolwiek innych współbieżnych coroutines.",
            distractors=[
                "Środowisko uruchomieniowe automatycznie przeniesie to wywołanie do puli wątków w tle (`threadpool`).",
                "Operacja automatycznie stanie się nieblokująca z uwagi na sam fakt deklaracji funkcji jako `async def`.",
                "Pętla zdarzeń pominie zawieszone zadanie i wywoła je ponownie w kolejnej iteracji po upływie zadanego czasu.",
            ],
            explanation="`asyncio` realizuje model kooperacyjnej wielozadaniowości w pojedynczym wątku systemu operacyjnego. Dopóki wykonywany kod nie napotka instrukcji `await` i nie odda sterowania, pętla zdarzeń nie może obsłużyć żadnego innego zadania ani odebrać danych z sieci. Samo zadeklarowanie funkcji jako `async def` nie czyni wywoływanego wewnątrz kodu synchronicznego nieblokującym. Wszelkie operacje blokujące I/O lub ciężkie obliczenia CPU należy jawnie delegować do puli wątków, np. za pomocą `asyncio.to_thread()`.",
        ),
        _make_q(
            id="py-eq-hash",
            category="Python",
            kind="theory",
            target_idx=3,  # D
            title="Kontrakt pomiędzy metodami `__eq__` i `__hash__`",
            prompt="Jaki kontrakt musi spełniać klasa w Pythonie, aby jej instancje mogły być poprawnie używane jako klucze słownika (`dict`) lub elementy zbioru (`set`)?",
            correct_answer="Obiekty równe według `__eq__` muszą posiadać identyczną wartość `__hash__`, a wartość ta nie może ulegać zmianie w czasie życia obiektu (obiekt musi być niemodyfikowalny / hashable).",
            distractors=[
                "Klasa musi dziedziczyć po typie `list`, aby słownik mógł dynamicznie modyfikować indeks w tablicy haszującej.",
                "Wartość `__hash__` musi być całkowicie unikalna w skali całej pamięci podręcznej interpretera (zerowe ryzyko kolizji).",
                "Metoda `__eq__` musi być zaimplementowana w taki sposób, aby porównywać wyłącznie typy wbudowane bez odwołań do atrybutów instancji.",
            ],
            explanation="Tablice haszujące w Pythonie wykorzystują funkcję `hash()` do szybkiego wyznaczenia indeksu kubełka w pamięci, a metodę `__eq__` do weryfikacji tożsamości klucza w przypadku kolizji hashy. Jeśli dwa obiekty są równe logicznie, ich hash bezwzględnie musi być identyczny, inaczej słownik nie odnajdzie wpisu. Ponadto zmiana stanu obiektu wpływająca na hash po umieszczeniu go w kolekcji sprawi, że wyląduje on w niewłaściwym kubełku i stanie się nieodnajdywalny. Z tego powodu kluczami słowników powinny być wyłącznie obiekty niezmienne (immutable).",
        ),
        _make_q(
            id="py-context-manager",
            category="Python",
            kind="theory",
            target_idx=0,  # A
            title="Protokół menedżera kontekstu (`__enter__` i `__exit__`)",
            prompt="W jaki sposób konstrukcja `with` i protokół menedżera kontekstu gwarantują deterministyczne zwalnianie zasobów?",
            correct_answer="Zapewniają bezwzględne wywołanie metody `__exit__` po opuszczeniu bloku kodu, przekazując do niej informacje o ewentualnym wyjątku i gwarantując sprzątanie nawet przy błędzie.",
            distractors=[
                "Wyciszają wszystkie wyjątki zgłoszone wewnątrz bloku kodu, zapobiegając przerwaniu działania aplikacji.",
                "Uruchamiają kod zawarty w bloku w izolowanym podprocesie systemu operacyjnego z automatycznym limitem pamięci.",
                "Przechowują deskryptor zasobu w globalnym rejestrze interpretera aż do zakończenia działania całego skryptu.",
            ],
            explanation="Menedżer kontekstu realizuje protokół złożony z dwóch metod: `__enter__` oraz `__exit__`. Metoda `__enter__` inicjalizuje zasób, a `__exit__` gwarantuje jego zwolnienie niezależnie od tego, czy blok zakończył się poprawnie, czy zgłoszono błąd. Do `__exit__` przekazywane są parametry wyjątku (`exc_type`, `exc_val`, `exc_tb`), co pozwala podjąć decyzję o jego stłumieniu (zwrócenie `True`) lub dalszej propagacji. Jest to kluczowy mechanizm chroniący przed wyciekami deskryptorów plików, połączeń bazodanowych czy blokad wątkowych.",
        ),
        _make_q(
            id="py-mro",
            category="Python",
            kind="theory",
            target_idx=1,  # B
            title="Kolejność rozwiązywania metod (MRO) i algorytm C3 Linearization",
            prompt="W jaki sposób Python ustala kolejność przeszukiwania klas w przypadku wielokrotnego dziedziczenia (np. przy problemie diamentowym)?",
            correct_answer="Wykorzystuje algorytm linearyzacji C3 (C3 Linearization), który zachowuje lokalną kolejność klas nadrzędnych oraz monotoniczność relacji w grafie dziedziczenia (`ClassName.mro()`).",
            distractors=[
                "Stosuje proste przeszukiwanie w głąb (Depth-First Search) od lewej do prawej bez sprawdzania spójności hierarchii.",
                "Wybiera zawsze metodę z tej klasy bazowej, która została zdefiniowana najwcześniej w czasie importu modułu.",
                "Wymusza jawne zdefiniowanie każdej metody w klasie pochodnej, zabraniając domyślnego dziedziczenia przy konfliktach nazw.",
            ],
            explanation="Linearyzacja C3 to zaawansowany algorytm tworzący uporządkowaną listę klas bazowych, dostępną pod atrybutem `Class.__mro__`. Gwarantuje on monotoniczność: podklasa zawsze występuje w łańcuchu przed swoimi przodkami, a kolejność klas zadeklarowana w definicji jest rygorystycznie zachowywana. Eliminuje to niejednoznaczności typowe dla problemu diamentowego w C++. W sytuacji, gdy zadeklarowana hierarchia dziedziczenia narusza spójność, interpreter natychmiast zgłasza wyjątek `TypeError` podczas tworzenia klasy.",
        ),
        _make_q(
            id="py-gc",
            category="Python",
            kind="theory",
            target_idx=2,  # C
            title="Zarządzanie pamięcią: zliczanie referencji a Garbage Collector cykli",
            prompt="W jaki sposób CPython zwalnia pamięć po obiektach i jak radzi sobie z cyklicznymi referencjami (`a.ref = b; b.ref = a`)?",
            correct_answer="Głównym mechanizmem jest natychmiastowe zliczanie referencji (reference counting), a cykliczne powiązania są periodycznie wykrywane i usuwane przez generacyjny moduł odśmiecania pamięci (`gc`).",
            distractors=[
                "CPython nie stosuje zliczania referencji, lecz korzysta wyłącznie z algorytmu Mark-and-Sweep uruchamianego przy wyczerpaniu pamięci RAM.",
                "Cykliczne referencje są automatycznie konwertowane na słabe referencje (`weakref`) w chwili ich utworzenia.",
                "Zwalnianie pamięci w CPythonie jest delegowane w całości do alokatora systemu operacyjnego `malloc/free` bez udziału interpretera.",
            ],
            explanation="W architekturze CPythona obiekt jest usuwany deterministycznie w chwili, gdy jego wewnętrzny licznik referencji (`ob_refcnt`) osiągnie zero. Problem pojawia się przy referencjach cyklicznych, gdzie obiekty wskazują na siebie nawzajem, uniemożliwiając wyzerowanie licznika nawet po utracie zmiennych zewnętrznych. Do rozwiązania tego problemu służy generacyjny moduł `gc`, który dzieli obiekty na trzy pokolenia (generacje 0, 1 i 2) i okresowo wykrywa nieosiągalne pętle referencji. Zrozumienie tego procesu jest kluczowe przy optymalizacji aplikacji o wysokiej przepustowości i unikaniu wycieków pamięci.",
        ),

        # =====================================================================
        # 2. FASTAPI — TEORIA
        # =====================================================================
        _make_q(
            id="fastapi-response-model",
            category="FastAPI",
            kind="theory",
            target_idx=3,  # D
            title="Rola parametru `response_model` w trasach FastAPI",
            prompt="Dlaczego parametr `response_model` w dekoratorach FastAPI jest krytyczny dla bezpieczeństwa i kontraktu API?",
            correct_answer="Konwertuje, waliduje i filtruje zwracane dane wyjściowe za pomocą Pydantic (ukrywając prywatne pola, np. hashe haseł) oraz automatycznie generuje specyfikację OpenAPI.",
            distractors=[
                "Odpowiada za automatyczne migrowanie schematów tabel w powiązanej relacyjnej bazie danych SQL.",
                "Wymusza asynchroniczną obsługę zapytania w osobnym procesie roboczym serwera ASGI.",
                "Wyłącza walidację parametrów wejściowych przesłanych w ciele żądania (request body).",
            ],
            explanation="`response_model` definiuje formalny kontrakt danych zwracanych przez endpoint. FastAPI przekazuje wynik zwrócony przez funkcję widoku do instancji wskazanego modelu Pydantic, co powoduje odrzucenie wszelkich pól niewymienionych w schemacie (np. hashy haseł czy kluczy wewnętrznych). Zapobiega to przypadkowemu wyciekowi wrażliwych atrybutów z obiektów bazodanowych bezpośrednio do odpowiedzi JSON. Jednocześnie schemat ten jest automatycznie eksportowany do dokumentacji Swagger UI i ReDoc, gwarantując jej bezwzględną zgodność z kodem.",
        ),
        _make_q(
            id="fastapi-dependency-injection",
            category="FastAPI",
            kind="theory",
            target_idx=0,  # A
            title="Mechanizm Dependency Injection (`Depends`) w FastAPI",
            prompt="W jaki sposób działa system wstrzykiwania zależności (`Depends`) w FastAPI i jak obsługuje poddrzewa zależności?",
            correct_answer="Buduje graf zależności (DAG) dla każdego żądania, rozwiązuje zależności rekurencyjnie (domyślnie keszując instancje w ramach jednego żądania dzięki `use_cache=True`) i wykonuje kod sprzątający po `yield`.",
            distractors=[
                "Tworzy globalne singletony przechowywane w pamięci procesu, współdzielone na zawsze pomiędzy wszystkimi użytkownikami.",
                "Wymaga manualnego rejestrowania kontenera IoC w osobnym pliku XML przed startem aplikacji.",
                "Działa wyłącznie dla funkcji synchronicznych, blokując użycie asynchronicznych coroutines jako dostawców zasobów.",
            ],
            explanation="Mechanizm Dependency Injection w FastAPI analizuje sygnatury funkcji i konstruuje skierowany graf acykliczny (DAG) zależności. Jeśli kilka podrzędnych zależności wymaga tego samego komponentu (np. sesji bazy), parametr `use_cache=True` zapewnia jednokrotne wykonanie fabryki w ramach danego żądania HTTP. Dodatkowo obsługa generatorów z instrukcją `yield` pozwala na implementację kodu czyszczącego (np. zamykanie transakcji), który wykonuje się bezwzględnie po wygenerowaniu odpowiedzi. Umożliwia to budowanie wysoce modularnych, łatwych w testowaniu i luźno powiązanych warstw backendu.",
        ),
        _make_q(
            id="fastapi-background-tasks",
            category="FastAPI",
            kind="theory",
            target_idx=1,  # B
            title="Zadania w tle (`BackgroundTasks`) a dedykowane kolejki zadań",
            prompt="Kiedy w aplikacji FastAPI wystarczy użyć wbudowanego `BackgroundTasks`, a kiedy konieczne jest wdrożenie brokera (np. Celery, ARQ, Redis)?",
            correct_answer="`BackgroundTasks` wykonuje zadania w tym samym procesie po wysłaniu odpowiedzi (dobre na proste I/O, np. e-mail); dla ciężkich obliczeń, zadań wymagających ponowień i odporności na awarie procesu potrzebny jest zewnętrzny worker z brokerem.",
            distractors=[
                "`BackgroundTasks` jest w pełni rozproszoną kolejką zadań zintegrowaną z klastrem Kubernetes bez potrzeby brokera.",
                "`BackgroundTasks` może być używane wyłącznie do zadań trwających dłużej niż kilka godzin, gdyż nie obciąża pamięci RAM serwera.",
                "FastAPI nie pozwala na integrację z Celery ani Redis, wymuszając korzystanie tylko z `BackgroundTasks`.",
            ],
            explanation="Wbudowane `BackgroundTasks` uruchamia funkcję w puli wątków lub jako coroutine bezpośrednio po odesłaniu odpowiedzi HTTP, ale w granicach procesu serwera ASGI. W przypadku awarii procesu, restartu kontenera lub wdrożenia nowej wersji oprogramowania, wszelkie zakolejkowane zadania przepadają bezpowrotnie. Brak tu również mechanizmów zaawansowanego ponawiania prób (backoff retries) oraz skalowania niezależnego od serwera HTTP. Dlatego w systemach produkcyjnych do krytycznych i długotrwałych procesów biznesowych bezwzględnie stosuje się brokery komunikatów i zewnętrzne procesy robocze (np. Celery czy ARQ).",
        ),

        # =====================================================================
        # 3. DJANGO — TEORIA
        # =====================================================================
        _make_q(
            id="django-queryset-lazy",
            category="Django",
            kind="theory",
            target_idx=2,  # C
            title="Leniwa ewaluacja (lazy evaluation) w Django ORM",
            prompt="W którym momencie Django ORM faktycznie wysyła zapytanie SQL do serwera bazy danych?",
            correct_answer="Dopiero w chwili ewaluacji QuerySetu, na przykład podczas iteracji w pętli (`for`), rzutowania na listę (`list()`), wywołania `len()` lub serializacji wyników.",
            distractors=[
                "Natychmiast po każdym wywołaniu metody filtrującej, takiej jak `.filter()` lub `.order_by()`.",
                "Dopiero po jawnym wywołaniu metody `.save()` na instancji powiązanego modelu.",
                "Jednorazowo w czasie uruchamiania procesu serwera Django podczas wczytywania modeli z `apps.py`.",
            ],
            explanation="Obiekty QuerySet w Django są z natury leniwe (lazy). Łączenie kolejnych metod filtrujących, takich jak `filter()`, `exclude()` czy `order_by()`, modyfikuje jedynie wewnętrzną strukturę reprezentującą zapytanie w pamięci Pythona bez kontaktu z bazą. Fizyczne zapytanie SQL jest generowane i wysyłane dopiero wtedy, gdy kod zażąda konkretnych danych (np. iteracja, rzutowanie do listy, indeksowanie). Taka architektura pozwala na optymalne łączenie warunków logicznych i minimalizuje liczbę zapytań wysyłanych do bazy.",
        ),
        _make_q(
            id="django-middleware-order",
            category="Django",
            kind="theory",
            target_idx=3,  # D
            title="Kolejność i cykl życia Middleware w Django",
            prompt="W jaki sposób Django przetwarza żądanie i odpowiedź przez łańcuch klas zdefiniowanych w liście `MIDDLEWARE`?",
            correct_answer="Żądanie przechodzi przez warstwy middleware od góry do dołu (top-down), a po wygenerowaniu odpowiedzi przez widok, odpowiedź wraca przez warstwy w odwrotnej kolejności (bottom-up).",
            distractors=[
                "Wszystkie klasy middleware wykonują się w pełni równolegle w osobnych procesach, a ich wyniki są łączone przez serwer WSGI.",
                "Kolejność w liście `MIDDLEWARE` nie ma znaczenia, ponieważ Django sortuje klasy na podstawie nazw metod alfabetycznie.",
                "Middleware wykonuje się wyłącznie raz na dobę podczas generowania statycznej pamięci podręcznej szablonów.",
            ],
            explanation="Lista `MIDDLEWARE` w Django implementuje wzorzec łańcucha odpowiedzialności (Chain of Responsibility), przypominający warstwy cebuli. W fazie żądania (request) kod wykonuje się ściśle od pierwszej do ostatniej klasy z listy, co wymaga poprawnej kolejności (np. `SecurityMiddleware` przed `AuthenticationMiddleware`). Z kolei po zakończeniu pracy widoku, obiekt odpowiedzi `response` wędruje w górę w dokładnie odwrotnym porządku (od dołu do góry). Błędne uporządkowanie klas w konfiguracji settings.py prowadzi do subtelnych błędów bezpieczeństwa lub braku dostępu do atrybutu `request.user`.",
        ),
        _make_q(
            id="django-signal-vs-save",
            category="Django",
            kind="theory",
            target_idx=0,  # A
            title="Sygnały Django (`post_save`) a nadpisanie metody `save()`",
            prompt="Jaki jest kluczowy kompromis architektoniczny pomiędzy sygnałami Django (`post_save`) a jawnym nadpisaniem metody `save()` w modelu?",
            correct_answer="Sygnały wprowadzają niejawny przepływ sterowania i utrudniają śledzenie kodu (ukryte efekty uboczne), natomiast nadpisanie `save()` jest jawne i bezpośrednie; ponadto sygnały nie wykonują się przy operacjach masowych (`bulk_create`, `update`).",
            distractors=[
                "Sygnały gwarantują asynchroniczne wykonanie kodu w osobnym klastrze serwerów, a metoda `save()` zawsze blokuje cały system operacyjny.",
                "Metoda `save()` nie ma dostępu do bazy danych, dlatego wszelkie relacje muszą być zapisywane wyłącznie za pomocą sygnałów.",
                "Sygnały są jedynym sposobem na walidację typów danych w formularzach Django Admin.",
            ],
            explanation="Sygnały w Django realizują wzorzec Publish-Subscribe, który odsprzęga nadawcę od odbiorcy, ale tworzy ukryty, trudny w nawigacji i debugowaniu przepływ sterowania. W warstwach domenowych Senior Developerzy preferują jawną logikę w metodzie `save()` modelu lub dedykowanych serwisach biznesowych. Istotnym ograniczeniem sygnałów jest również to, że metody masowe ORM (np. `bulk_create` czy `update`) całkowicie je pomijają ze względów wydajnościowych. Z tego względu sygnały są rekomendowane głównie do integracji z zewnętrznymi, nienależącymi do nas aplikacjami Django.",
        ),

        # =====================================================================
        # 4. FLASK — TEORIA
        # =====================================================================
        _make_q(
            id="flask-factory",
            category="Flask",
            kind="theory",
            target_idx=1,  # B
            title="Wzorzec fabryki aplikacji (`create_app`) we Flasku",
            prompt="Dlaczego stosowanie wzorca Application Factory (`create_app`) jest standardem w dojrzałych projektach Flask?",
            correct_answer="Zapobiega tworzeniu globalnej instancji aplikacji, umożliwiając tworzenie odizolowanych instancji z odmienną konfiguracją (np. do testów jednostkowych z bazą w pamięci).",
            distractors=[
                "Automatycznie kompiluje kod Pythona do kodu maszynowego C za pomocą biblioteki Cython.",
                "Wymusza asynchroniczny model pętli zdarzeń kompatybilny z ASGI bez potrzeby używania WSGI.",
                "Zapewnia przechowywanie stanu całej bazy danych wyłącznie w sesjach po stronie przeglądarki klienta.",
            ],
            explanation="Stworzenie globalnego obiektu `app = Flask(__name__)` utrudnia zarządzanie konfiguracją i prowadzi do problemu wycieku stanu pomiędzy testami jednostkowymi. Wzorzec fabryki `create_app(config)` pozwala na powoływanie wielu odizolowanych instancji aplikacji z parametrami dostosowanymi do środowiska (deweloperskie, produkcyjne, testowe). Ułatwia również modularne podpinanie rozszerzeń za pomocą metody `init_app()`, co stanowi fundament czystej architektury. Jest to rekomendowany wzorzec zalecany w oficjalnej dokumentacji Pallets/Flask.",
        ),
        _make_q(
            id="flask-context",
            category="Flask",
            kind="theory",
            target_idx=2,  # C
            title="Rozróżnienie między Application Context a Request Context",
            prompt="Jaka jest różnica pomiędzy kontekstem aplikacji (`app_context`) a kontekstem żądania (`request_context`) we Flasku?",
            correct_answer="`request_context` przechowuje dane powiązane z bieżącym żądaniem HTTP (`request`, `session`), natomiast `app_context` daje dostęp do konfiguracji aplikacji (`current_app`, `g`) i może istnieć bez aktywnego żądania HTTP (np. w komendach CLI lub zadaniach Celery).",
            distractors=[
                "`request_context` zarządza połączeniami z bazą danych, a `app_context` odpowiada wyłącznie za renderowanie szablonów Jinja2.",
                "Oba konteksty są identyczne i zostały rozdzielone tylko w celu zachowania zgodności z Pythonem 2.",
                "`app_context` jest tworzony tylko raz w czasie kompilacji, a `request_context` jest współdzielony przez wszystkich użytkowników.",
            ],
            explanation="Flask wykorzystuje mechanizm proxy kontekstowego oparty na zmiennych lokalnych wątku (`werkzeug.local.LocalProxy`). Kontekst żądania jest tworzony dynamicznie dla każdego połączenia HTTP i niszczony po wysłaniu odpowiedzi. Kontekst aplikacji pozwala na współdzielenie konfiguracji i obiektów bazodanowych poza protokołem HTTP, co jest niezbędne przy uruchamianiu komend CLI (`flask run`) czy zadań asynchronicznych. Próba użycia zasobów aplikacji bez otwartego bloku `with app.app_context():` skutkuje błędem czasu wykonania.",
        ),
        _make_q(
            id="flask-blueprints",
            category="Flask",
            kind="theory",
            target_idx=3,  # D
            title="Modularyzacja architektury za pomocą Blueprintów",
            prompt="Do czego służą Blueprinty (`Blueprint`) we frameworku Flask?",
            correct_answer="Do logicznego podziału aplikacji na niezależne, reużywalne moduły z własnymi trasami, szablonami, plikami statycznymi oraz prefiksami URL.",
            distractors=[
                "Do definiowania schematów tabel i generowania automatycznych migracji bazy danych SQLite.",
                "Do uruchamiania aplikacji Flask w architekturze mikrousług bez użycia serwera HTTP.",
                "Do automatycznego skalowania kontenerów w środowisku chmurowym AWS.",
            ],
            explanation="Blueprinty we Flasku pełnią rolę izolowanych modułów architektonicznych w większych systemach webowych. Umożliwiają one definiowanie grup widoków, filtrów szablonów oraz obsługi błędów bez konieczności bezpośredniego wiązania ich z konkretną instancją aplikacji na poziomie importu. Każdy Blueprint może definiować własny prefiks adresu URL (np. `/auth` lub `/api/v1`), co zapobiega konfliktom nazw tras w projektach zespołowych. Są one następnie rejestrowane w głównej fabryce aplikacji za pomocą metody `app.register_blueprint()`.",
        ),

        # =====================================================================
        # 5. SQL — TEORIA
        # =====================================================================
        _make_q(
            id="sql-index",
            category="SQL",
            kind="theory",
            target_idx=0,  # A
            title="Zasada działania indeksu B-Tree i koszt zapisu",
            prompt="Jaki jest fundamentalny kompromis wydajnościowy związany ze stosowaniem indeksów B-Tree w relacyjnych bazach danych?",
            correct_answer="Przyspieszają operacje wyszukiwania, złączeń i sortowania (redukując złożoność z O(N) do O(log N)), lecz zwiększają narzut czasowy operacji zapisu (`INSERT`, `UPDATE`, `DELETE`) z uwagi na konieczność balansowania drzewa indeksu i zajmują dodatkową przestrzeń dyskową.",
            distractors=[
                "Spowalniają wszystkie operacje `SELECT`, ponieważ silnik bazy musi najpierw przeszukać pełną tabelę przed użyciem indeksu.",
                "Uniemożliwiają stosowanie transakcji bazodanowych i wyłączają gwarancje spójności ACID dla tabeli.",
                "Automatycznie usuwają powtarzające się rekordy z bazy i modyfikują klucze obce.",
            ],
            explanation="Indeksy B-Tree organizują klucze w zrównoważone drzewa poszukiwań, co pozwala silnikowi relacyjnemu odnaleźć konkretne rekordy w kilku operacjach I/O zamiast kosztownego pełnego skanowania tabeli (Seq Scan). Jednakże każda operacja modyfikująca dane tabeli wymusza synchroniczną aktualizację wszystkich powiązanych struktur indeksowych i potencjalne dzielenie stron (page splits) na dysku. W systemach transakcyjnych OLTP o wysokim natężeniu zapisu nadmierna liczba indeksów drastycznie obniża przepustowość bazy. Dlatego Senior Developer tworzy indeksy precyzyjnie pod rzeczywiste wzorce zapytań (często wielokolumnowe lub częściowe).",
        ),
        _make_q(
            id="sql-transaction",
            category="SQL",
            kind="theory",
            target_idx=1,  # B
            title="Właściwości transakcji bazodanowej (ACID)",
            prompt="Co dokładnie oznaczają poszczególne filary reguły ACID w relacyjnych bazach danych?",
            correct_answer="Atomowość (wszystko albo nic), Spójność (przejście między prawidłowymi stanami bazy), Izolacja (niezależność współbieżnych transakcji) oraz Trwałość (gwarancja zachowania zatwierdzonych zmian po awarii zasilania/systemu).",
            distractors=[
                "Asynchroniczność (operacje bez blokowania), Ciągłość (brak przerw serwisowych), Integracja (współpraca z API) oraz Dystrybucja (rozproszenie w klastrze).",
                "Automatyczne buforowanie zapytań SELECT w pamięci podręcznej serwera aplikacji w celu ominięcia dysku.",
                "Gwarancja optymalizacji zapytań SQL przez kompilator JIT bez udziału planera bazy danych.",
            ],
            explanation="Zasady ACID stanowią fundament bezpieczeństwa danych w systemach RDBMS. Atomowość gwarantuje, że w razie jakiegokolwiek błędu wszystkie operacje transakcji zostaną całkowicie cofnięte (Rollback). Spójność pilnuje egzekwowania reguł biznesowych i więzów integralności zdefiniowanych na poziomie schematu bazy. Izolacja decyduje o widoczności zmian pomiędzy równolegle pracującymi transakcjami, a Trwałość (oparta o mechanizm Write-Ahead Log) zapewnia przetrwanie zatwierdzonych transakcji na wypadek awarii sprzętowej.",
        ),
        _make_q(
            id="sql-left-join",
            category="SQL",
            kind="theory",
            target_idx=2,  # C
            title="Zachowanie złączenia `LEFT JOIN` i semantyka NULL",
            prompt="W jaki sposób złączenie `LEFT JOIN` traktuje rekordy z lewej tabeli, które nie posiadają odpowiedników w prawej tabeli?",
            correct_answer="Zwraca wszystkie rekordy z tabeli po lewej stronie, a dla kolumn pochodzących z prawej tabeli podstawia wartości `NULL`.",
            distractors=[
                "Całkowicie odrzuca wiersze bez dopasowania, zachowując się identycznie jak standardowy `INNER JOIN`.",
                "Zwraca błąd naruszenia więzów spójności relacyjnej i przerywa wykonywanie zapytania SQL.",
                "Podstawia wartości domyślne typu zero (0) lub pusty ciąg tekstowy zamiast wartości `NULL`.",
            ],
            explanation="Klauzula `LEFT JOIN` (zewnętrzne złączenie lewostronne) gwarantuje, że żaden rekord z lewej tabeli nie zostanie utracony w wynikowym zestawie danych. Jeżeli warunek złączenia `ON` nie znajdzie powiązanego wiersza w prawej tabeli, wszystkie kolumny z prawej strony przyjmują wartość `NULL`. Jest to fundamentalna różnica względem `INNER JOIN`, który zwraca wyłącznie część wspólną obu zbiorów. Konstrukcję `LEFT JOIN` w połączeniu z warunkiem `WHERE right_table.id IS NULL` powszechnie stosuje się do efektywnego wykrywania rekordów niepowiązanych.",
        ),
        _make_q(
            id="sql-isolation",
            category="SQL",
            kind="theory",
            target_idx=3,  # D
            title="Poziomy izolacji transakcji i anomalie współbieżności",
            prompt="Przed jakimi anomaliami chroni poziom izolacji `REPEATABLE READ` w silnikach bazodanowych (np. PostgreSQL/MySQL)?",
            correct_answer="Chroni przed brudnymi odczytami (Dirty Reads) oraz niepowtarzalnymi odczytami (Non-repeatable Reads), gwarantując, że wielokrotny odczyt tego samego wiersza w transakcji zwróci identyczne dane.",
            distractors=[
                "Chroni przed wyczerpaniem pamięci RAM serwera i automatycznie restartuje zawieszone połączenia.",
                "Zapobiega błędom składniowym w zapytaniach SQL generowanych dynamicznie przez warstwę ORM.",
                "Wycisza wszystkie zakleszczenia (Deadlocks), zezwalając na równoległy zapis tego samego rekordu bez blokad.",
            ],
            explanation="Standard ANSI SQL definiuje cztery poziomy izolacji transakcji o rosnącym stopniu rygorystyczności. Poziom `REPEATABLE READ` zapobiega brudnym odczytom (odczyt danych niezatwierdzonych przez inną transakcję) oraz niepowtarzalnym odczytom (zmiana danych wiersza przez zatwierdzoną zewnętrzną transakcję w trakcie trwania naszej). W silniku PostgreSQL poziom ten wykorzystuje migawki MVCC i chroni również przed większością odczytów widm (Phantom Reads). Wybór poziomu izolacji jest kompromisem pomiędzy gwarancjami spójności a ryzykiem blokad i zakleszczeń (deadlocks).",
        ),
        _make_q(
            id="sql-optimistic-locking",
            category="SQL",
            kind="theory",
            target_idx=0,  # A
            title="Blokowanie optymistyczne a pesymistyczne w systemach transakcyjnych",
            prompt="Jaka jest różnica w implementacji blokowania optymistycznego (Optimistic Concurrency Control) względem blokowania pesymistycznego (`SELECT ... FOR UPDATE`)?",
            correct_answer="Blokowanie optymistyczne zakłada rzadkie konflikty — nie blokuje wierszy w bazie, lecz weryfikuje pole wersji/timestamp przy zapisie (`WHERE version = :old_version`); blokowanie pesymistyczne natychmiast zakłada fizyczną blokadę na rekordzie w bazie.",
            distractors=[
                "Blokowanie optymistyczne działa wyłącznie w bazach NoSQL, a pesymistyczne jest zarezerwowane dla silników relacyjnych.",
                "Blokowanie pesymistyczne eliminuje konieczność stosowania transakcji ACID w relacyjnej bazie danych.",
                "Blokowanie optymistyczne polega na automatycznym ponawianiu zapytań w nieskończoność bez sprawdzania stanu bazy.",
            ],
            explanation="Blokowanie pesymistyczne (`SELECT ... FOR UPDATE`) natychmiast rezerwuje wiersz na poziomie silnika bazy danych, zmuszając inne współbieżne transakcje do oczekiwania w kolejce. Może to prowadzić do wąskich gardeł wydajnościowych oraz zakleszczeń przy długo trwających operacjach. Z kolei blokowanie optymistyczne pozwala na równoległe odczyty bez nakładania blokad, weryfikując wersję rekordu dopiero w momencie instrukcji `UPDATE`. Jeśli liczba zaktualizowanych wierszy wynosi zero, oznacza to wystąpienie wyścigu, a aplikacja może ponowić transakcję z nowymi danymi.",
        ),

        # =====================================================================
        # 6. REST — TEORIA
        # =====================================================================
        _make_q(
            id="rest-idempotency",
            category="REST",
            kind="theory",
            target_idx=1,  # B
            title="Idempotentność metod HTTP w architekturze REST",
            prompt="Co dokładnie oznacza właściwość idempotentności metody HTTP w projektowaniu interfejsów API?",
            correct_answer="Wielokrotne wysłanie identycznego żądania wywołuje dokładnie taki sam skutek dla stanu zasobów na serwerze jak pojedyncze wykonanie (np. metody `GET`, `PUT`, `DELETE`).",
            distractors=[
                "Metoda zwraca dokładnie taki sam czas odpowiedzi (w milisekundach) niezależnie od obciążenia serwera.",
                "Żądanie HTTP nie może zawierać żadnych nagłówków uwierzytelniających ani parametrów zapytania.",
                "Odpowiedź serwera jest zawsze buforowana w pamięci podręcznej przeglądarki na czas nieokreślony.",
            ],
            explanation="Idempotentność oznacza, że skutek uboczny wykonania serii identycznych żądań jest tożsamy ze skutkiem wykonania pojedynczego żądania. Metody takie jak `GET`, `HEAD`, `PUT` oraz `DELETE` są z definicji idempotentne (np. ponowne usunięcie usuniętego już zasobu nie zmienia stanu bazy). Z kolei metoda `POST` tworzy zazwyczaj nowy zasób podrzędny, dlatego jej ponowienie prowadzi do duplikacji danych. Cecha ta ma kluczowe znaczenie przy projektowaniu odpornych na błędy sieciowe systemów rozproszonych, umożliwiając bezpieczne automatyczne ponawianie zapytań.",
        ),
        _make_q(
            id="http-401-403",
            category="REST",
            kind="theory",
            target_idx=2,  # C
            title="Semantyka kodów HTTP: 401 Unauthorized a 403 Forbidden",
            prompt="W jakiej sytuacji architekt REST API powinien zwrócić kod 401, a kiedy kod 403?",
            correct_answer="Kod 401 oznacza brak lub niepoprawne dane uwierzytelniające (klient jest anonimowy); kod 403 oznacza, że tożsamość klienta została zweryfikowana, lecz nie posiada on uprawnień do żądanego zasobu.",
            distractors=[
                "Kod 401 stosuje się wyłącznie dla zapytań POST, podczas gdy kod 403 dotyczy wyłącznie zapytań GET i DELETE.",
                "Kod 401 oznacza błąd wewnętrzny serwera aplikacji, a 403 informuje o braku szukanego zasobu w bazie.",
                "Oba kody są tożsame według specyfikacji RFC 7231 i wybór zależy wyłącznie od preferencji zespołu.",
            ],
            explanation="Rozróżnienie pomiędzy kodami 401 i 403 wynika z rozgraniczenia uwierzytelniania (Authentication) od autoryzacji (Authorization). Kod 401 (Unauthorized / Unauthenticated) sygnalizuje, że żądanie nie zawiera ważnych poświadczeń tożsamości, a serwer powinien wskazać metodę logowania w nagłówku `WWW-Authenticate`. Kod 403 (Forbidden) wskazuje, że serwer wie, kim jest użytkownik, ale jego uprawnienia (np. rola RBAC) zabraniają dostępu do danego zasobu. Prawidłowe stosowanie tych kodów jest kluczowe dla aplikacji klienckich, aby wiedziały, czy przekierować użytkownika do ekranu logowania, czy wyświetlić informację o braku praw.",
        ),
        _make_q(
            id="rest-hateoas",
            category="REST",
            kind="theory",
            target_idx=3,  # D
            title="Poziom 3 dojrzałości Richardsona i mechanizm HATEOAS",
            prompt="Czym charakteryzuje się zasada HATEOAS (Hypermedia As The Engine Of Application State) w dojrzałym REST API?",
            correct_answer="Odpowiedź serwera zawiera nie tylko dane zasobu, ale również hiperłącza (linki) wskazujące akcje i powiązane zasoby, które klient może wykonać w bieżącym stanie aplikacji.",
            distractors=[
                "Wymusza użycie protokołu gRPC i binarnej serializacji Protocol Buffers zamiast formatu JSON.",
                "Zabrania stosowania jakichkolwiek metod HTTP poza metodą POST z przekazywaniem nagłówka akcji.",
                "Wymaga, aby cała dokumentacja API była generowana wyłącznie statycznie w plikach PDF.",
            ],
            explanation="Zasada HATEOAS stanowi najwyższy, trzeci poziom w modelu dojrzałości REST stworzonym przez Leonarda Richardsona. Klient otrzymujący reprezentację zasobu (np. zamówienia) dostaje w odpowiedzi nie tylko jego status, ale także relacje z adresami URL do kolejnych dozwolonych przejść stanów (np. link do opłacenia, modyfikacji lub anulowania). Dzięki temu klient nie musi posiadać sztywno zakodowanej wiedzy o strukturze adresów URL w backendzie, lecz odkrywa możliwości dynamicznie w trakcie działania. Zapewnia to wysoki poziom odsprzężenia i ułatwia ewolucję kontraktów API bez łamania kompatybilności.",
        ),

        # =====================================================================
        # 7. AI / RAG — TEORIA
        # =====================================================================
        _make_q(
            id="ai-rag",
            category="AI / RAG",
            kind="theory",
            target_idx=0,  # A
            title="Architektura RAG (Retrieval-Augmented Generation)",
            prompt="Jaki problem rozwiązuje architektura RAG w systemach produkcyjnych opartych na modelach językowych (LLM)?",
            correct_answer="Wzbogaca zapytanie do modelu o precyzyjnie wyszukane fragmenty z zewnętrznych źródeł wiedzy, redukując halucynacje i umożliwiając dostęp do prywatnych/aktualnych danych bez kosztownego dotrenowywania wag.",
            distractors=[
                "Automatycznie dotrenowuje wagi modelu w locie podczas każdego zapytania klienta za pomocą algorytmu wstecznej propagacji.",
                "Gwarantuje matematyczny brak jakichkolwiek błędów i w 100% eliminuje konieczność testowania promptów.",
                "Zastępuje relacyjne bazy danych i całkowicie eliminuje potrzebę stosowania języka SQL w architekturze backendu.",
            ],
            explanation="Architektura RAG rozdziela odpowiedzialność na dwa niezależne komponenty: wyszukiwanie wiedzy (Retrieval) oraz generowanie odpowiedzi (Generation). W pierwszym etapie silnik wyszukuje najbardziej relewantne dokumenty z zewnętrznego magazynu (np. bazy wektorowej lub hybrydowej). Następnie wyselekcjonowane fragmenty są dołączane do promptu jako ugruntowany kontekst dla modelu językowego. Rozwiązanie to pozwala na natychmiastowe aktualizowanie bazy wiedzy firmy bez konieczności kosztownego i skomplikowanego dotrenowywania sieci neuronowej.",
        ),
        _make_q(
            id="ai-chunking",
            category="AI / RAG",
            kind="theory",
            target_idx=1,  # B
            title="Strategie chunkowania tekstu a okno kontekstu",
            prompt="Dlaczego odpowiedni dobór rozmiaru fragmentu tekstu (`chunk size`) i nakładania (`chunk overlap`) ma kluczowe znaczenie w systemach RAG?",
            correct_answer="Zbyt małe chunki tracą kontekst semantyczny zdania, a zbyt duże rozmywają wektor embeddingu i marnują okno kontekstu modelu; `overlap` zapobiega ucięciu myśli na granicy podziału.",
            distractors=[
                "Chunking służy wyłącznie do szyfrowania danych algorytmem AES-256 przed zapisem w bazie wektorowej.",
                "Modele językowe wymagają, aby każdy dokument w bazie składał się dokładnie z jednego tokena.",
                "Rozmiar chunka nie ma wpływu na jakość wyszukiwania, o ile włączona jest kompresja gzip.",
            ],
            explanation="Dzielenie długich dokumentów na mniejsze fragmenty (tzw. chunking) to krytyczny krok w przygotowywaniu indeksu wiedzy dla systemów RAG. Jeśli fragmenty będą zbyt małe, wektor embeddingowy nie uchwyci szerszego sensu wypowiedzi, co drastycznie obniży jakość odpowiedzi. Z kolei zbyt duże chunki rozmywają precyzję wektora i szybko zapełniają limit okna kontekstowego modelu LLM. Zastosowanie nakładania (overlap) zabezpiecza przed utratą spójności logicznej zdań rozciętych na granicy dwóch kolejnych chunków.",
        ),
        _make_q(
            id="ai-embeddings",
            category="AI / RAG",
            kind="theory",
            target_idx=2,  # C
            title="Wektory cech (Embeddings) i metryki podobieństwa",
            prompt="W jaki sposób bazy wektorowe (np. pgvector, Qdrant, Chroma) porównują semantyczne podobieństwo zapytań do dokumentów?",
            correct_answer="Przekształcają tekst w gęste wektory liczb zmiennoprzecinkowych za pomocą modelu embeddingowego i obliczają odległość w przestrzeni wielowymiarowej (np. podobieństwo kosinusowe, odległość euklidesową, dot product).",
            distractors=[
                "Porównują liczbę wystąpień identycznych liter w obu tekstach za pomocą algorytmu Levenshteina.",
                "Wykonują proste porównanie hashy SHA-256 wygenerowanych z całego dokumentu.",
                "Wyszukują dokumenty wyłącznie na podstawie dokładnego dopasowania podciągów w indeksie B-Tree.",
            ],
            explanation="Modele embeddingowe (np. OpenAI text-embedding-3 czy modele open-source BGE) przekształcają ciągi tekstowe w wielowymiarowe wektory liczb rzeczywistych. Wektory tekstów o zbliżonym znaczeniu semantycznym układają się blisko siebie w tej przestrzeni matematycznej. Baza wektorowa oblicza miarę bliskości (np. podobieństwo kosinusowe mierzące kąt pomiędzy wektorami) z wykorzystaniem zoptymalizowanych indeksów HNSW lub IVFFlat. Dzięki temu system potrafi odnaleźć właściwe dokumenty nawet wtedy, gdy użytkownik zada pytanie bez użycia identycznych słów kluczowych.",
        ),

        # =====================================================================
        # 8. CI/CD — TEORIA
        # =====================================================================
        _make_q(
            id="cicd-ci-cd",
            category="CI/CD",
            kind="theory",
            target_idx=3,  # D
            title="Podstawowe cele i różnice: CI vs CD",
            prompt="Co odróżnia praktykę Continuous Integration (CI) od Continuous Delivery / Continuous Deployment (CD)?",
            correct_answer="CI koncentruje się na częstym scalaniu kodu do gałęzi głównej wraz z automatycznymi testami i lintowaniem; CD automatyzuje przygotowanie wydania na środowiska (Delivery wymaga zgody, Deployment wdraża na produkcję automatycznie).",
            distractors=[
                "CI jest procesem manualnym przeprowadzanym przez testerów, a CD to automatyczne tworzenie dokumentacji API.",
                "CI dotyczy wyłącznie tworzenia repozytoriów git, podczas gdy CD odpowiada za konfigurację DNS domeny.",
                "Nie ma między nimi żadnej różnicy merytorycznej — to dwa synonimy opisujące ten sam skrypt bashowy.",
            ],
            explanation="Continuous Integration (CI) polega na regularnym, zautomatyzowanym integrowaniu zmian programistów do wspólnego repozytorium i natychmiastowym uruchamianiu testów jednostkowych oraz analizy statycznej. Continuous Delivery (CD) gwarantuje, że każda zielona wersja kodu z pipeline'u może zostać bezpiecznie wdrożona na środowisko produkcyjne za pomocą jednego kliknięcia. Z kolei Continuous Deployment eliminuje konieczność ręcznej autoryzacji — każdy pomyślnie zweryfikowany commit trafia bezpośrednio do użytkowników końcowych. Zrozumienie tych różnic jest fundamentem nowoczesnej kultury DevOps w zespołach inżynierskich.",
        ),
        _make_q(
            id="cicd-security",
            category="CI/CD",
            kind="theory",
            target_idx=0,  # A
            title="Bezpieczeństwo pipeline'u: SAST, DAST i skanowanie zależności",
            prompt="Jakie narzędzia w pipeline CI/CD odpowiadają za wykrywanie znanych luk bezpieczeństwa (CVE) w bibliotekach zewnętrznych Pythona?",
            correct_answer="Narzędzia typu Software Composition Analysis (SCA), takie jak `pip-audit`, `safety` czy `Trivy`, które weryfikują listę zależności z bazami podatności (CVE/Advisory).",
            distractors=[
                "Lintery kodu źródłowego typu `flake8` lub `black`, które usuwają błędy składniowe w plikach `.py`.",
                "Formatowania plików JSON za pomocą pre-commit hooków bez kontaktu z bazami danych.",
                "Narzędzia pomiaru pokrycia kodu testami jednostkowymi (`pytest-cov`).",
            ],
            explanation="Praktyka DevSecOps zakłada automatyzację weryfikacji bezpieczeństwa na wczesnych etapach cyklu wytwarzania oprogramowania (Shift-Left Security). Narzędzia SCA skanują pliki zależności (np. `requirements.txt` lub `poetry.lock`), porównując ich wersje z oficjalnymi bazami znanych podatności CVE. Uzupełniają je skanery statyczne SAST (np. `bandit`), które analizują kod pod kątem wycieków sekretów czy podatności na ataki typu injection. Zablokowanie pipeline'u w razie wykrycia krytycznej luki zapobiega wypuszczeniu podatnego artefaktu na środowiska produkcyjne.",
        ),

        # =====================================================================
        # 9. DOCKER — TEORIA
        # =====================================================================
        _make_q(
            id="docker-image-container",
            category="Docker",
            kind="theory",
            target_idx=1,  # B
            title="Struktura warstwowa obrazu a proces kontenera",
            prompt="Czym pod maską różni się obraz Dockera od uruchomionego kontenera?",
            correct_answer="Obraz to zbiór niezmiennych warstw systemu plików tylko do odczytu (read-only layers); kontener to wyizolowany proces systemowy (cgroups, namespaces) z dołączoną cienką warstwą zapisu (read-write layer).",
            distractors=[
                "Obraz jest pełną maszyną wirtualną z własnym emulowanym jądrem systemu, a kontener to plik konfiguracyjny YAML.",
                "Obraz i kontener to tożsame pliki wykonywalne, różniące się wyłącznie rozszerzeniem pliku w katalogu `/var/lib/docker`.",
                "Kontener jest szablonem kodu źródłowego, z którego programista manualnie kompiluje wynikowy obraz.",
            ],
            explanation="Obraz Dockera to spakowany, niezmienny zestaw warstw (layers) przygotowany w procesie budowania, przeznaczony wyłącznie do odczytu. Kontener to po prostu standardowy proces systemu operacyjnego Linux, uruchomiony z ograniczeniami zasobów (cgroups) i wyizolowaną widocznością systemu plików oraz sieci (namespaces). Na wierzchu niemodyfikowalnych warstw obrazu kontener otrzymuje ulotną warstwę zapisu typu copy-on-write. Po usunięciu kontenera warstwa ta bezpowrotnie przepada, co wymusza stosowanie wolumenów do przechowywania danych trwałych.",
        ),
        _make_q(
            id="docker-layers",
            category="Docker",
            kind="theory",
            target_idx=2,  # C
            title="Mechanizm buforowania warstw (Layer Caching) w Dockerfile",
            prompt="Dlaczego kolejność instrukcji w pliku Dockerfile ma fundamentalny wpływ na czas budowania obrazu w CI/CD?",
            correct_answer="Zmiana w dowolnej warstwie unieważnia pamięć podręczną (cache) dla wszystkich kolejnych instrukcji w dół pliku; dlatego rzadko zmieniane zależności instaluje się przed kopiowaniem często edytowanego kodu.",
            distractors=[
                "Instrukcje w Dockerfile są wykonywane od dołu do góry, co wymaga umieszczania polecenia `ENTRYPOINT` na samym początku.",
                "Docker buforuje wyłącznie ostatnią instrukcję `CMD`, a wszystkie wcześniejsze kroki są zawsze budowane od zera.",
                "Kolejność instrukcji nie ma znaczenia, ponieważ silnik budowania samoczynnie grupuje i sortuje polecenia `RUN`.",
            ],
            explanation="Silnik budowania obrazów Dockera analizuje instrukcje sekwencyjnie i sprawdza sumy kontrolne plików używanych w danym kroku. Gdy dana warstwa ulegnie modyfikacji, pamięć podręczna (cache) dla tej instrukcji oraz wszystkich kolejnych zostaje automatycznie unieważniona. Dobrą praktyką seniora jest umieszczanie na początku instrukcji rzadko zmiennych (np. kopiowanie `requirements.txt` i `pip install`), a dopiero na samym końcu kodu źródłowego (`COPY . .`). Taki podział sprawia, że codzienne modyfikacje kodu w Pythonie nie wymagają czasochłonnego ponownego pobierania pakietów z sieci.",
        ),

        # =====================================================================
        # 10. KUBERNETES — TEORIA
        # =====================================================================
        _make_q(
            id="kubernetes-probes",
            category="Kubernetes",
            kind="theory",
            target_idx=3,  # D
            title="Cykl życia Poda: Readiness, Liveness oraz Startup Probes",
            prompt="W jaki sposób sonda `readinessProbe` różni się od `livenessProbe` w zarządzaniu ruchem w klastrze Kubernetes?",
            correct_answer="`readinessProbe` informuje, czy Pod może bezpiecznie przyjmować ruch z powiązanego Service (jej błąd odłącza Pod z endpointów ruchu bez restartu); błąd `livenessProbe` uznaje kontener za zawieszony i powoduje jego restart przez kubelet.",
            distractors=[
                "`readinessProbe` natychmiast usuwa cały klaster i restartuje węzeł roboczy, a `livenessProbe` służy wyłącznie do pomiaru zużycia CPU.",
                "Obie sondy wykonują się wyłącznie raz podczas budowania obrazu kontenera w rejestrze.",
                "`readinessProbe` służy do sprawdzania uprawnień bazy danych, a `livenessProbe` zarządza certyfikatami SSL.",
            ],
            explanation="Mechanizm sond w Kubernetesie rozdziela weryfikację dostępności aplikacji od jej wewnętrznej żywotności. Sonda `readinessProbe` decyduje o tym, czy kube-proxy powinno kierować ruch sieciowy do danego Poda; jej niepowodzenie (np. podczas rozgrzewania cache) usuwa Pod z listy endpointów bez zabijania procesu. Z kolei `livenessProbe` ma na celu wykrywanie stanów martwych (np. zakleszczenie wątków lub wyciek pamięci) i w razie błędu restartuje kontener. Zastosowanie sondy liveness do sprawdzania zewnętrznych zależności (np. bazy) jest kardynalnym błędem, który podczas awarii bazy doprowadzi do restartu wszystkich Podów naraz.",
        ),
        _make_q(
            id="kubernetes-controllers",
            category="Kubernetes",
            kind="theory",
            target_idx=0,  # A
            title="Pętla uzgadniania (Reconciliation Loop) w kontrolerach Kubernetes",
            prompt="Na czym polega fundamentalny wzorzec działania kontrolerów w Kubernetesie (np. Deployment, ReplicaSet)?",
            correct_answer="Działają w pętli uzgadniania (Reconciliation Loop), która nieustannie porównuje stan bieżący klastra z zadeklarowanym stanem pożądanym (Desired State) i wykonuje akcje korygujące w razie rozbieżności.",
            distractors=[
                "Wykonują skrypty crona wewnątrz kontenerów co 60 sekund i restartują cały węzeł w razie błędu.",
                "Zastępują konieczność stosowania baz danych, przechowując stan aplikacji w rejestrach procesora.",
                "Działają wyłącznie reaktywnie na polecenia `kubectl` wydawane ręcznie przez administratora.",
            ],
            explanation="Kubernetes opiera się na deklaratywnym modelu zarządzania zasobami. Użytkownik definiuje stan pożądany w pliku manifestu YAML, który trafia do bazy etcd. Kontrolery pracują w nieustannej pętli uzgadniania: odczytują stan bieżący z klastra, porównują go ze stanem pożądanym i aplikują niezbędne zmiany (np. tworzą brakujące Pody po awarii węzła). Dzięki temu system wykazuje właściwości samonaprawiające (self-healing), przywracając stabilność środowiska bez konieczności interwencji inżyniera.",
        ),

        # =====================================================================
        # PRAKTYKA (WYBIERANE 4 W KAŻDYM ZESTAWIE DZIENNYM)
        # =====================================================================
        _make_q(
            id="practice-default-list",
            category="Python",
            kind="practice",
            target_idx=1,  # B
            title="Korekta modyfikowalnego argumentu domyślnego",
            prompt="Funkcja gromadzi dane w liście domyślnej pomiędzy kolejnymi wywołaniami. W jaki sposób poprawnie usunąć ten błąd?",
            correct_answer="Zastosować `def dodaj(x, lista=None)` i wewnątrz funkcji utworzyć nową listę `lista = []`, jeśli przekazana wartość to `None`.",
            distractors=[
                "Zamienić domyślną listę w nagłówku funkcji na pusty zbiór `set()`.",
                "Dodać deklarację `global lista` wewnątrz ciała funkcji.",
                "Zwracać `lista.copy()` na końcu funkcji, pozostawiając pustą listę w nagłówku.",
            ],
            explanation="Zastosowanie wartości `None` jako domyślnego argumentu to idiomatyczny wzorzec w języku Python. Pozwala to na utworzenie nowej instancji listy w pamięci wyłącznie w momencie wywołania funkcji, o ile użytkownik nie dostarczył własnego obiektu. Zwrócenie `lista.copy()` bez zmiany sygnatury nie rozwiązuje problemu, ponieważ argument domyślny nadal będzie rósł w kolejnych wywołaniach. Rozwiązanie to jest w pełni bezpieczne i powszechnie oczekiwane na rozmowach technicznych.",
        ),
        _make_q(
            id="practice-lru",
            category="Python",
            kind="practice",
            target_idx=2,  # C
            title="Projekt struktury pamięci podręcznej LRU",
            prompt="Projektujesz pamięć podręczną typu Least Recently Used (LRU) o średniej złożoności czasowej O(1) dla operacji `get` oraz `put`. Które rozwiązanie jest optymalne?",
            correct_answer="Słownik (`dict`) do szybkiego wyszukiwania powiązany z listą dwukierunkową (np. `collections.OrderedDict`) do zarządzania kolejnością użycia.",
            distractors=[
                "Zwykła lista przeszukiwana liniowo przy każdym wywołaniu operacji `get`.",
                "Niemodyfikowalna krotka (`tuple`) kopiowana na nowo przy każdym zapisie `put`.",
                "Kolejka FIFO bez aktualizowania pozycji elementu po udanym odczycie `get`.",
            ],
            explanation="Implementacja pamięci podręcznej LRU wymaga natychmiastowego dostępu do elementów oraz możliwości szybkiej reorganizacji kolejności ich użycia. Słownik (tablica haszująca) zapewnia odczyt i zapis w średnim czasie O(1), a lista dwukierunkowa pozwala w czasie O(1) przenieść odczytany element na początek lub usunąć najstarszy wpis z końca. W bibliotece standardowej Pythona idealną strukturą łączącą obie te cechy jest `collections.OrderedDict`. W codziennej pracy Senior Developer najczęściej stosuje gotowy dekorator `@functools.lru_cache`.",
        ),
        _make_q(
            id="practice-async-gather",
            category="Python",
            kind="practice",
            target_idx=3,  # D
            title="Współbieżne wykonywanie niezależnych operacji asynchronicznych",
            prompt="Aplikacja musi wykonać trzy niezależne zapytania HTTP i zagregować ich wyniki. Które podejście w `asyncio` wykona je współbieżnie?",
            correct_answer="Użycie funkcji `asyncio.gather(*coroutines)` oczekującej na zakończenie wszystkich zadań.",
            distractors=[
                "Wywołanie każdej coroutine sekwencyjnie z użyciem `time.sleep()` pomiędzy nimi.",
                "Zadeklarowanie funkcji jako `async def` i wywołanie coroutine bez użycia `await`.",
                "Użycie blokady `threading.Lock()` do synchronizacji zadań w pojedynczym wątku.",
            ],
            explanation="Funkcja `asyncio.gather()` przyjmuje zestaw coroutines, rejestruje je jako współbieżne zadania w bieżącej pętli zdarzeń i zawiesza wykonanie do momentu ukończenia wszystkich operacji. Pozwala to na jednoczesne oczekiwanie na odpowiedzi z trzech zewnętrznych serwisów sieciowych, redukując łączny czas wykonania do czasu najwolniejszego zapytania. W nowszych wersjach Pythona (3.11+) alternatywnym, bezpiecznym podejściem jest użycie menedżera `asyncio.TaskGroup`. Z kolei sekwencyjne awaitowanie kolejnych zapytań zniwelowałoby zalety programowania asynchronicznego.",
        ),
        _make_q(
            id="practice-python-stream",
            category="Python",
            kind="practice",
            target_idx=0,  # A
            title="Strumieniowe czytanie dużego pliku",
            prompt="Jak efektywnie policzyć niepuste wiersze w pliku tekstowym o rozmiarze 10 GB, nie doprowadzając do wyczerpania pamięci RAM?",
            correct_answer="Otworzyć plik w bloku `with` i iterować bezpośrednio po obiekcie pliku linia po linii (`for line in plik:`).",
            distractors=[
                "Wczytać całą zawartość pliku metodą `read()` i podzielić go metodą `.splitlines()`.",
                "Wczytać wszystkie wiersze naraz do tablicy za pomocą metody `readlines()`.",
                "Skopiować całą zawartość do globalnej zmiennej tekstowej przed rozpoczęciem zliczania.",
            ],
            explanation="Obiekt pliku zwrócony przez funkcję `open()` jest w Pythonie buforowanym iteratorem. Pętla `for line in plik:` pobiera z dysku tylko pojedynczy wiersz naraz, dzięki czemu zużycie pamięci operacyjnej jest stałe i znikome bez względu na to, czy plik ma 10 MB, czy 100 GB. Użycie metod takich jak `read()` lub `readlines()` ładuje cały plik do pamięci w jednej strukturze, co przy wielogigabajtowym pliku natychmiast wywoła błąd `MemoryError`. Jest to klasyczny przykład przewagi przetwarzania strumieniowego nad ładowaniem całościowym.",
        ),
        _make_q(
            id="practice-fastapi-async",
            category="FastAPI",
            kind="practice",
            target_idx=1,  # B
            title="Integracja biblioteki synchronicznej w FastAPI",
            prompt="Endpoint FastAPI korzysta z zewnętrznej biblioteki, która udostępnia wyłącznie synchroniczne, blokujące API. Jak zadeklarować trasę, aby nie blokować asynchronicznej pętli zdarzeń?",
            correct_answer="Zdefiniować funkcję endpointu jako standardowe `def` — FastAPI automatycznie uruchomi ją w dedykowanej puli wątków roboczych.",
            distractors=[
                "Oznaczyć funkcję jako `async def` i wywołać blokującą bibliotekę bez użycia słowa kluczowego `await`.",
                "Uruchomić funkcję blokującą przez `asyncio.run()` wewnątrz endpointu zadeklarowanego jako `async def`.",
                "Zwiększyć liczbę workerów serwera Uvicorn bez wprowadzania zmian w sygnaturze endpointu.",
            ],
            explanation="FastAPI posiada inteligentny mechanizm obsługi funkcji widoków. Jeśli endpoint zostanie zdefiniowany jako zwykłe `def`, framework automatycznie przekieruje jego wykonanie do puli wątków (`anyio.to_thread.run_sync`), chroniąc główną pętlę zdarzeń przed zablokowaniem. Zadeklarowanie takiego endpointu jako `async def` spowodowałoby wykonanie synchronicznej, blokującej operacji bezpośrednio w wątku pętli, paraliżując obsługę innych zapytań. Jest to jedna z najważniejszych zasad projektowania wydajnych serwisów w FastAPI.",
        ),
        _make_q(
            id="practice-fastapi-session",
            category="FastAPI",
            kind="practice",
            target_idx=2,  # C
            title="Zarządzanie cyklem życia sesji bazy w FastAPI",
            prompt="W jaki sposób bezpiecznie udostępnić endpointom sesję bazy danych na czas obsługi żądania, gwarantując jej zwrot do puli po zakończeniu?",
            correct_answer="Zastosować zależność (`Depends`) opartą na generatorze z instrukcją `yield`, otwierającą sesję w bloku `try...finally`.",
            distractors=[
                "Utworzyć pojedynczą sesję globalną na poziomie modułu i współdzielić ją pomiędzy wszystkimi żądaniami.",
                "Otwierać sesję w konstruktorze aplikacji i zamykać ją dopiero przy zatrzymaniu serwera.",
                "Zamykać sesję tylko w sytuacji, gdy endpoint zakończy się kodem błędu HTTP 500.",
            ],
            explanation="Wstrzykiwanie zależności oparte na generatorze z instrukcją `yield` działa w FastAPI jak zintegrowany menedżer kontekstu dla żądania HTTP. Kod przed `yield` pobiera sesję z puli połączeń i przekazuje ją do funkcji endpointu, natomiast sekcja `finally` po `yield` wykonuje się zawsze po wygenerowaniu odpowiedzi. Zapewnia to bezpieczne zamknięcie sesji lub jej zwrot do puli nawet wtedy, gdy w trakcie obsługi żądania wystąpi nieobsłużony błąd. Współdzielenie sesji jako zmiennej globalnej doprowadziłoby do wyścigów i uszkodzenia stanu transakcji pomiędzy współbieżnymi zapytaniami.",
        ),
        _make_q(
            id="practice-fastapi-status",
            category="FastAPI",
            kind="practice",
            target_idx=3,  # D
            title="Prawidłowy kod statusu HTTP przy tworzeniu zasobu",
            prompt="Endpoint REST API tworzy nowy profil użytkownika po pomyślnej walidacji i zwraca utworzone dane. Jaki kod statusu HTTP powinien zwrócić?",
            correct_answer="201 Created",
            distractors=[
                "204 No Content (nawet jeśli odpowiedź zawiera utworzony obiekt)",
                "301 Moved Permanently",
                "503 Service Unavailable",
            ],
            explanation="Zgodnie ze standardem protokołu HTTP (RFC 7231), poprawną odpowiedzią na żądanie `POST`, którego celem było utworzenie nowego zasobu, jest kod `201 Created`. Do odpowiedzi można również dołączyć nagłówek `Location` wskazujący bezpośredni adres URL do nowo utworzonego obiektu. Kod `204 No Content` stosuje się wyłącznie wtedy, gdy operacja zakończyła się sukcesem, ale ciało odpowiedzi jest puste (np. przy usunięciu zasobu). Dbałość o precyzyjne kody statusu to podstawa czytelnego i profesjonalnego API.",
        ),
        _make_q(
            id="practice-django-nplus1",
            category="Django",
            kind="practice",
            target_idx=0,  # A
            title="Eliminacja problemu N+1 Queries w relacji ForeignKey",
            prompt="Serializator zamówień odczytuje dla każdego rekordu pole `order.customer.name` (relacja `ForeignKey`), generując setki zapytań SQL. Jak zoptymalizować to zapytanie?",
            correct_answer="Dodać `.select_related('customer')` do początkowego zapytania QuerySet zamówień.",
            distractors=[
                "Wywołać `.save()` dla każdego klienta przed rozpoczęciem serializacji.",
                "Zamienić relację ForeignKey na zwykłe pole tekstowe CharField.",
                "Zastosować metodę `.prefetch_related()` pojedynczo na każdej instancji modelu.",
            ],
            explanation="Problem N+1 zapytań występuje wtedy, gdy odczyt kolekcji N elementów generuje dodatkowe zapytanie do bazy dla każdego pojedynczego wiersza w celu pobrania powiązanej encji. Metoda `select_related()` instruuje Django ORM, aby wykonał złączenie SQL `JOIN` już w początkowym zapytaniu, pobierając powiązane obiekty w jednej operacji sieciowej. Stosuje się ją dla relacji jednoznacznych, takich jak `ForeignKey` czy `OneToOneField`. Pozwala to zredukować liczbę zapytań z setek do dokładnie jednego, drastycznie przyspieszając czas odpowiedzi aplikacji.",
        ),
        _make_q(
            id="practice-django-prefetch",
            category="Django",
            kind="practice",
            target_idx=1,  # B
            title="Optymalizacja relacji Many-to-Many w Django ORM",
            prompt="Widok wyświetla listę wpisów na blogu wraz z przypisanymi tagami (relacja `ManyToManyField`). Jak ograniczyć liczbę zapytań SQL?",
            correct_answer="Dodać `.prefetch_related('tags')` do bazowego QuerySetu wpisów.",
            distractors=[
                "Użyć `.select_related('tags')` dla relacji wiele-do-wielu.",
                "Wykonać osobną metodę `.save()` dla każdego pobieranego taga.",
                "Wyłączyć mechanizm leniwego ładowania w konfiguracji globalnej.",
            ],
            explanation="Relacje wielowartościowe, takie jak `ManyToManyField` czy odwrotne klucze obce (`reverse ForeignKey`), nie mogą być optymalnie obsłużone pojedynczym złączeniem `JOIN` bez multiplikacji wierszy w bazie. Z tego powodu Django udostępnia metodę `prefetch_related()`, która wykonuje osobne, zoptymalizowane zapytanie z klauzulą `IN` dla powiązanych obiektów. Następnie Django ORM łączy pobrane rekordy w pamięci Pythona, eliminując problem wielokrotnych odpytań bazy. Przekłada się to na stałą, przewidywalną liczbę zapytań niezależnie od wielkości zbioru danych.",
        ),
        _make_q(
            id="practice-flask-factory",
            category="Flask",
            kind="practice",
            target_idx=2,  # C
            title="Testy tras Flask w izolowanym środowisku",
            prompt="Jak prawidłowo przetestować trasę aplikacji Flask z odrębną konfiguracją testową i tymczasową bazą danych?",
            correct_answer="Utworzyć aplikację za pomocą fabryki `create_app(test_config)` i wysyłać żądania za pośrednictwem `app.test_client()`.",
            distractors=[
                "Zmodyfikować słownik globalnej konfiguracji produkcyjnej aplikacji w trakcie trwania testu.",
                "Uruchomić zewnętrzny serwer developerski na publicznym porcie i wysyłać zapytania biblioteką requests.",
                "Współdzielić produkcyjną bazę danych, pomijając konfigurację testową.",
            ],
            explanation="Wykorzystanie fabryki aplikacji `create_app()` pozwala na przekazanie dedykowanego słownika z parametrami testowymi (np. `TESTING=True` oraz baza SQLite w pamięci RAM). Wbudowane narzędzie `app.test_client()` symuluje żądania HTTP bezpośrednio na poziomie interfejsu WSGI, co eliminuje narzut sieciowy i konieczność uruchamiania fizycznego serwera. Każdy test może dzięki temu działać na świeżej, wyizolowanej instancji aplikacji, co gwarantuje determinizm i powtarzalność wyników. Modyfikowanie globalnych zmiennych produkcyjnych w trakcie testów jest antywzorcem prowadzącym do trudnych w wykryciu błędów.",
        ),
        _make_q(
            id="practice-sql-transfer",
            category="SQL",
            kind="practice",
            target_idx=3,  # D
            title="Bezpieczna realizacja transferu środków w transakcji",
            prompt="Jak wyeliminować ryzyko ujemnego salda i częściowego wykonania przelewu przy współbieżnych żądaniach w relacyjnej bazie danych?",
            correct_answer="W ramach pojedynczej transakcji wykonać warunkową aktualizację salda (`UPDATE ... WHERE balance >= kwota`), sprawdzić liczbę zmodyfikowanych wierszy i w razie błędu wycofać transakcję.",
            distractors=[
                "Wykonać dwa niezależne zapytania UPDATE w trybie autocommit bez użycia transakcji.",
                "Odczytać saldo w Pythonie, po czym bezwarunkowo wykonać oba zapytania UPDATE.",
                "Zwiększyć limit czasu połączenia do bazy danych i całkowicie zrezygnować z blokad transakcyjnych.",
            ],
            explanation="Operacje finansowe wymagają bezwzględnej atomowości i ochrony przed zjawiskiem wyścigu (race condition). Wykonanie warunkowego zapytania `UPDATE accounts SET balance = balance - :kwota WHERE id = :id AND balance >= :kwota` jest operacją atomową po stronie silnika bazy danych. Jeśli liczba zaktualizowanych rekordów wynosi zero, oznacza to brak wystarczających środków, a transakcja powinna zostać natychmiast wycofana (`ROLLBACK`). Sprawdzenie salda w kodzie Pythona przed wykonaniem aktualizacji jest podatne na błąd Time-of-check to time-of-use (TOCTOU).",
        ),
        _make_q(
            id="practice-sql-explain",
            category="SQL",
            kind="practice",
            target_idx=0,  # A
            title="Diagnoza wolnego zapytania SQL",
            prompt="Zapytanie SQL filtrujące dużą tabelę wykonuje się zbyt wolno. Jaki powinien być pierwszy profesjonalny krok diagnostyczny?",
            correct_answer="Przeanalizować plan wykonania zapytania za pomocą polecenia `EXPLAIN (ANALYZE)` i sprawdzić obecność pełnych skanów tabeli (Seq Scan).",
            distractors=[
                "Dodać prewencyjnie indeksy na wszystkich kolumnach występujących w tabeli.",
                "Zwiększyć liczbę dozwolonych połączeń w puli bazy danych bez analizy zapytania.",
                "Zastąpić filtrowanie WHERE pętlą wykonującą filtrowanie po stronie kodu Pythona.",
            ],
            explanation="Polecenie `EXPLAIN ANALYZE` uruchamia zapytanie i zwraca rzeczywisty plan wykonania przygotowany przez planer bazy danych. Pokazuje ono czasy trwania poszczególnych węzłów, użyte indeksy, algorytmy złączeń (np. Hash Join czy Nested Loop) oraz to, czy doszło do kosztownego pełnego skanowania tabeli (Sequential Scan). Dopiero na podstawie tych danych Senior Developer podejmuje decyzję o dodaniu precyzyjnego indeksu, zmianie kolejności złączeń lub refaktoryzacji zapytania. Dodawanie indeksów 'na ślepo' jest kardynalnym błędem obniżającym wydajność operacji zapisu.",
        ),
        _make_q(
            id="practice-idempotency",
            category="REST",
            kind="practice",
            target_idx=1,  # B
            title="Obsługa ponowień żądań POST za pomocą klucza idempotencji",
            prompt="Klient API ponawia żądanie POST po upływie limitu czasu (timeout), co grozi utworzeniem zduplikowanego zamówienia. Jakie rozwiązanie jest najbezpieczniejsze?",
            correct_answer="Wymusić unikalny klucz idempotencji (`Idempotency-Key`), zapisać go w bazie atomowo z wynikiem i zwracać zapisaną odpowiedź w przypadku ponowienia.",
            distractors=[
                "Zwiększyć timeout po stronie serwera do wartości uniemożliwiającej przekroczenie czasu.",
                "Ignorować wszystkie kolejne żądania przychodzące z danego adresu IP.",
                "Zastąpić metodę POST metodą GET z przekazywaniem danych zamówienia w parametrach URL.",
            ],
            explanation="Nagłówek `Idempotency-Key` (standard spopularyzowany m.in. przez Stripe) to unikalny identyfikator generowany przez klienta dla danej operacji biznesowej. Przy pierwszym odebraniu żądania serwer przetwarza operację w transakcji i zapisuje wygenerowaną odpowiedź powiązaną z tym kluczem w trwałym magazynie. Jeśli klient z powodu timeoutu ponowi zapytanie z tym samym kluczem, serwer odnajduje wcześniejszy wpis i odsyła gotową odpowiedź bez ponownego obciążania konta użytkownika. Jest to sprawdzony wzorzec architektoniczny gwarantujący odporność systemów płatności i zamówień na niestabilność sieci.",
        ),
        _make_q(
            id="practice-ci-flaky",
            category="CI/CD",
            kind="practice",
            target_idx=2,  # C
            title="Diagnoza niestabilnego testu (flaky test)",
            prompt="Jeden z testów integracyjnych przechodzi lokalnie, lecz sporadycznie zawodzi w środowisku CI. Co stanowi właściwe rozwiązanie problemu?",
            correct_answer="Przeanalizować logi z CI, zidentyfikować źródło niedeterminizmu (np. zależność od czasu, stan współdzielonej bazy) i usunąć przyczynę.",
            distractors=[
                "Dodać mechanizm nieskończonych powtórzeń testu (`retry`), aby ukryć sporadyczne błędy.",
                "Wyłączyć test na stałe bez diagnozowania przyczyny niepowodzenia.",
                "Zmienić asercję w teście na sprawdzającą wyłącznie fakt wywołania funkcji.",
            ],
            explanation="Testy niestabilne (tzw. flaky tests) niszczą zaufanie zespołu inżynierskiego do pipeline'u CI/CD i często prowadzą do ignorowania rzeczywistych regresji kodu. Powszechnymi przyczynami niedeterminizmu są wyścigi współbieżności, nieoczyszczony stan bazy danych pomiędzy testami, zależność od strefy czasowej lub sztywne wywołania `sleep()`. Dodawanie automatycznych powtórzeń (retries) jedynie maskuje problem zamiast go naprawić. Właściwym podejściem jest zebranie szczegółowych logów, odtworzenie warunków CI i usunięcie pierwotnej przyczyny braku powtarzalności.",
        ),
        _make_q(
            id="practice-docker-cache",
            category="Docker",
            kind="practice",
            target_idx=3,  # D
            title="Optymalne wykorzystanie pamięci podręcznej warstw w Dockerze",
            prompt="Każda zmiana w pliku z kodem aplikacji powoduje ponowną, długą instalację wszystkich zależności przez `pip`. Jak poprawnie uporządkować instrukcje w Dockerfile?",
            correct_answer="Najpierw skopiować plik zależności (`requirements.txt`) i uruchomić `pip install`, a dopiero w późniejszym kroku skopiować często modyfikowany kod źródłowy.",
            distractors=[
                "Kopiować cały projekt instrukcją `COPY . .` przed każdą instrukcją `RUN`.",
                "Całkowicie wyłączyć pamięć podręczną (cache) dla wszystkich kroków w procesie budowania.",
                "Przenieść instalację zależności z etapu budowania obrazu do skryptu startowego kontenera.",
            ],
            explanation="Mechanizm pamięci podręcznej warstw w Dockerze (Layer Caching) weryfikuje sumy kontrolne plików dla instrukcji `COPY` oraz ciągi znaków dla poleceń `RUN`. Zmiana zawartości pliku w danym kroku bezwzględnie unieważnia cache dla wszystkich kolejnych operacji w pliku Dockerfile. Kopiując najpierw wyłącznie plik manifestu zależności (`requirements.txt`) i uruchamiając instalację pakietów, sprawiamy, że Docker wykorzysta istniejącą warstwę cache dopóki nie dodamy nowej biblioteki. Dopiero po zainstalowaniu zależności kopiujemy właściwy kod źródłowy aplikacji (`COPY . .`), co skraca czas budowania w CI z kilku minut do ułamków sekund.",
        ),
        _make_q(
            id="practice-kubernetes-pending",
            category="Kubernetes",
            kind="practice",
            target_idx=0,  # A
            title="Diagnoza Poda w stanie Pending",
            prompt="Nowo wdrożony Pod w klastrze Kubernetes pozostaje w stanie `Pending`. Od czego najlepiej rozpocząć diagnozę?",
            correct_answer="Wykonać `kubectl describe pod <nazwa>` i sprawdzić sekcję zdarzeń (`Events`), w szczególności wymagania zasobów CPU/RAM, wolumeny PVC oraz reguły planowania.",
            distractors=[
                "Zmienić konfigurację sondy gotowości (`readinessProbe`), która działa dopiero po uruchomieniu kontenera.",
                "Usunąć wszystkie limity zasobów w całym klastrze.",
                "Zwiększyć liczbę replik w Deploymentcie bez weryfikacji zdarzeń.",
            ],
            explanation="Stan `Pending` oznacza, że Pod został zaakceptowany przez klastrowy serwer API, lecz scheduler nie był w stanie przypisać go do żadnego dostępnego węzła roboczego (Node). Najczęstszymi przyczynami są niewystarczające zasoby procesora lub pamięci (CPU/Memory Requests), niespełnione reguły kolokacji (NodeAffinity, PodAntiAffinity) lub oczekiwanie na zamontowanie wolumenu PersistentVolumeClaim. Polecenie `kubectl describe pod` w sekcji `Events` zawiera bezpośrednie komunikaty planera wyjaśniające, dlaczego żaden węzeł nie spełnia wymagań Poda. Jest to podstawowy i najszybszy krok diagnostyczny każdego inżyniera Kubernetes.",
        ),
        _make_q(
            id="practice-rag-eval",
            category="AI / RAG",
            kind="practice",
            target_idx=1,  # B
            title="Ewaluacja jakości komponentów w systemie RAG",
            prompt="W systemie RAG zmodyfikowano model embeddingowy oraz strategię podziału dokumentów na fragmenty (chunking). Jak profesjonalnie zmierzyć wpływ tej zmiany?",
            correct_answer="Zastosować oznaczony zbiór testowy i zmierzyć oddzielnie jakość wyszukiwania (np. Recall@k, Hit Rate) oraz jakość wygenerowanych odpowiedzi (np. ugruntowanie w faktach i poprawność).",
            distractors=[
                "Ocenić wyłącznie czas odpowiedzi na jednym losowo wpisanym zapytaniu ręcznym.",
                "Zwiększyć temperaturę modelu LLM i uznać bardziej rozbudowaną gramatycznie odpowiedź za lepszą.",
                "Pominąć ocenę trafności wyszukiwania, jeśli wygenerowana odpowiedź brzmi przekonująco.",
            ],
            explanation="Profesjonalna ewaluacja architektury RAG wymaga rozdzielenia testów na dwa niezależne etapy: warstwę wyszukiwania (Retrieval) oraz warstwę generacji (Generation). W warstwie wyszukiwania mierzy się, czy odnalezione fragmenty zawierają poszukiwaną odpowiedź, stosując metryki takie jak Recall@k, Hit Rate czy MRR (Mean Reciprocal Rank). Z kolei w warstwie generacji weryfikuje się ugruntowanie wypowiedzi w faktach (Faithfulness/Groundedness) oraz brak halucynacji za pomocą frameworków takich jak Ragas czy TruLens. Ręczna ocena pojedynczych zapytań jest wysoce subiektywna i uniemożliwia wykrycie regresji w systemach produkcyjnych.",
        ),
    ]
