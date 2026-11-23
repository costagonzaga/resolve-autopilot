# Resolve Autopilot

Automatize o **DaVinci Resolve Studio** com Python e [Claude Code](https://claude.com/claude-code):
monte a timeline a partir de uma pasta de takes, aplique um visual consistente, pré-misture o áudio
(voz tratada, música que abaixa quando há fala, efeitos sonoros nos cortes) e renderize.

Deixe rodando e revise o resultado de manhã. A mídia original nunca é alterada nem apagada.

▶️ **[Veja o vídeo de 37 segundos](https://github.com/costagonzaga/resolve-autopilot/releases/tag/v0.1.0)** (anexado à release)

🇺🇸 [Read in English](README.md)

## O que é isso, em português simples

Quem edita vídeo no DaVinci Resolve repete as mesmas tarefas: colocar os takes em ordem, dar
zoom e cor, acertar o volume da voz e da música, pôr efeitos e títulos animados. O Resolve Autopilot
faz essas tarefas por comandos, e funciona junto com o Claude Code (uma IA que programa): você
descreve o que quer, ele monta uma **cópia** da sua edição, e você revisa de manhã. Seus vídeos
originais nunca são alterados.

## Quer ajudar? Leva 30 segundos

Este projeto é novo e **precisa de gente de verdade usando e comentando**. Você não precisa saber programar:

1. ⭐ **Dê uma estrela.** Clique em **Star**, no topo direito desta página (precisa de uma conta
   gratuita no GitHub, que se cria em 2 minutos). Isso ajuda o projeto a ser encontrado.
2. 💬 **Comente.** Abra a [issue "Diga oi"](https://github.com/costagonzaga/resolve-autopilot/issues/4),
   escreva uma frase (por exemplo: "edito vídeo no DaVinci e quero testar") e clique em **Comment**.
3. 🧪 **Teste, se usa Mac ou Linux.** As issues
   [#1](https://github.com/costagonzaga/resolve-autopilot/issues/1) e
   [#2](https://github.com/costagonzaga/resolve-autopilot/issues/2) explicam o passo a passo.
4. 📤 **Mande o link** para quem edita vídeo no DaVinci.

Obrigado, de verdade.

## O que tem

- **Conexão** com o Resolve no Windows, macOS e Linux, com mensagem clara quando ele não responde.
- **Montagem da timeline** a partir de takes numerados (`01.mp4`, `02.mp4`...).
- **Visual**: zoom alternado e cor (CDL) numa timeline *duplicada*, com marcador em cada corte.
- **Pré-mix de áudio com ffmpeg** (a API não controla volume): voz reconstruída dos originais e limpa,
  música com ducking, efeitos alinhados ao corte, tudo no volume-alvo (LUFS).
- **Render** pela fila do Resolve, aplicando as configurações uma a uma.
- **Inspetor somente leitura** que mostra as timelines em JSON para o assistente de IA.
- **Skill do Claude Code** em `skills/resolve-autopilot`.

## Requisitos

- DaVinci Resolve **Studio** aberto com um projeto.
- Resolve: *Preferences > System > General > External scripting using: Local*.
- Python 3.9+ e [ffmpeg](https://ffmpeg.org/) (ou `pip install imageio-ffmpeg`).

## Instalar e usar

```bash
pip install "resolve-autopilot[ffmpeg] @ git+https://github.com/costagonzaga/resolve-autopilot"
resolve-autopilot check
resolve-autopilot build ./takes "Meu reel"
resolve-autopilot look "Meu reel" "Meu reel v2"
resolve-autopilot mix "Meu reel v2" musica.wav ./audio --sfx whoosh1.wav whoosh2.wav
resolve-autopilot add-audio "Meu reel v2" ./audio
resolve-autopilot render "Meu reel v2" ./saida reel --size 1080 1920
```

## Motion: Resolve + Remotion

O Resolve edita, o [Remotion](https://www.remotion.dev) desenha os gráficos animados e o
`resolve-autopilot` faz a ponte: renderiza um clipe **ProRes 4444 transparente** no tamanho e
no frame rate da sua timeline e o coloca numa trilha nova acima da V1 de uma timeline *duplicada*.
Seus takes nunca são tocados.

```bash
cd motion && npm install && cd ..        # uma vez; precisa de Node.js 20+
resolve-autopilot motion "Meu reel v2" "Meu reel v3" \
    --lead "o segredo é" --word "CONSISTÊNCIA" --at 3.5 --duration 2.5
```

O template (`motion/src/TitleHighlight.tsx`) tem uma linha branca pequena e uma palavra grande
amarela em Poppins que entra com mola e some com fade. Copie-o para criar os seus.

## Situação

Versão inicial (v0.1), testada no Windows com Resolve Studio 21. Os caminhos de macOS e Linux seguem
a documentação da Blackmagic, mas **não foram testados**: relatos e correções são bem-vindos.
Veja o [CONTRIBUTING.md](CONTRIBUTING.md).

## Licença

MIT. DaVinci Resolve é marca da Blackmagic Design; este projeto não tem ligação com ela.
