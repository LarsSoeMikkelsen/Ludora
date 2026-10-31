/* Ludora installer page: Secure Boot / MOK enrollment.
 *
 * Shown by the notesqml@secureboot instance. With Secure Boot on, explains
 * the one-time MokManager enrollment on first start (password: ludora,
 * set by the ludora_secureboot job). With it off, says there is nothing
 * to do. Calamares cannot hide a page conditionally.
 *
 * QML cannot run commands, so the Secure Boot state comes from
 * /tmp/ludora-secureboot.ini ([secureboot] enabled=true|false), written by
 * ludora-sb-state before Calamares starts.
 *
 * Language: Calamares sets QLocale's default to the language picked on the
 * welcome page and calls onActivate() each time this page is shown.
 * Same 14 translations as netinstall.conf; anything else falls back to en.
 * The MokManager menu items and its prompt stay in English on purpose:
 * that is what the blue screen shows.
 */
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtCore

Item {
    id: page

    Settings {
        id: sbIni
        location: "file:///tmp/ludora-secureboot.ini"
        category: "secureboot"
    }

    readonly property bool sbEnabled: {
        var v = sbIni.value("enabled", "false")
        return v === true || v === "true"
    }

    property string lang: pickLang(Qt.locale().name)

    function pickLang(name) {
        if (texts[name] !== undefined)
            return name
        var base = name.split("_")[0]
        return texts[base] !== undefined ? base : "en"
    }

    // Called by Calamares when the page is shown
    function onActivate() {
        lang = pickLang(Qt.locale().name)
    }

    function html(t) {
        if (!sbEnabled)
            return "<h2>" + t.offTitle + "</h2>" + t.offBody
        var steps = "<ol>"
        for (var i = 0; i < t.steps.length; i++)
            steps += "<li>" + t.steps[i] + "</li>"
        steps += "</ol>"
        return "<h2>" + t.onTitle + "</h2>" + t.intro + t.lead + steps + t.keyboard + t.missed
    }

    readonly property var texts: ({
        "en": {
            offTitle: "Secure Boot",
            offBody: "<p>Secure Boot is <b>off</b> on this PC, so there is nothing to do here. Click <b>Next</b>.</p><p>If you turn Secure Boot on later, first run <tt>sudo ludora-secureboot setup</tt> in Ludora and follow its instructions, then turn it on.</p>",
            onTitle: "Secure Boot is on: one extra step on first start",
            intro: "<p>Ludora's gaming kernel is not signed by Microsoft, so the installer creates a signing key for this PC. Your PC has to approve that key <b>once</b>, the first time it starts after the installation.</p>",
            lead: "<p>On that first start a <b>blue screen</b> appears. Do this:</p>",
            steps: [
                "When it says <i>Press any key to perform MOK management</i>, press a key <b>within 10 seconds</b>.",
                "Choose <b>Enroll MOK</b>.",
                "Choose <b>Continue</b>.",
                "Choose <b>Yes</b>.",
                "Type the password <b>ludora</b> and press Enter. Nothing is shown while you type.",
                "Choose <b>Reboot</b>. Ludora then starts normally, from now on without this screen."
            ],
            keyboard: "<p>The blue screen uses a US keyboard layout. On an AZERTY keyboard (e.g. French), type the last letter of <b>ludora</b> with the <b>Q</b> key.</p>",
            missed: "<p><b>Missed the blue screen?</b> Ludora will not start while Secure Boot is on. Turn Secure Boot off in your firmware settings, start Ludora, run <tt>sudo ludora-secureboot setup</tt>, restart, complete the blue screen, then turn Secure Boot back on.</p>"
        },
        "de": {
            offTitle: "Secure Boot",
            offBody: "<p>Secure Boot ist auf diesem PC <b>ausgeschaltet</b>, hier ist also nichts zu tun. Klicken Sie auf <b>Weiter</b>.</p><p>Wenn Sie Secure Boot später einschalten, führen Sie vorher in Ludora <tt>sudo ludora-secureboot setup</tt> aus und folgen Sie den Anweisungen.</p>",
            onTitle: "Secure Boot ist eingeschaltet: ein zusätzlicher Schritt beim ersten Start",
            intro: "<p>Der Gaming-Kernel von Ludora ist nicht von Microsoft signiert. Deshalb erstellt das Installationsprogramm einen Signaturschlüssel für diesen PC. Ihr PC muss diesen Schlüssel <b>einmalig</b> bestätigen, beim ersten Start nach der Installation.</p>",
            lead: "<p>Bei diesem ersten Start erscheint ein <b>blauer Bildschirm</b>. Gehen Sie so vor:</p>",
            steps: [
                "Wenn <i>Press any key to perform MOK management</i> erscheint, drücken Sie <b>innerhalb von 10 Sekunden</b> eine Taste.",
                "Wählen Sie <b>Enroll MOK</b>.",
                "Wählen Sie <b>Continue</b>.",
                "Wählen Sie <b>Yes</b>.",
                "Geben Sie das Passwort <b>ludora</b> ein und drücken Sie Enter. Während der Eingabe wird nichts angezeigt.",
                "Wählen Sie <b>Reboot</b>. Ludora startet dann normal, ab jetzt ohne diesen Bildschirm."
            ],
            keyboard: "<p>Der blaue Bildschirm verwendet ein US-Tastaturlayout. Auf einer AZERTY-Tastatur (z. B. Französisch) geben Sie den letzten Buchstaben von <b>ludora</b> mit der Taste <b>Q</b> ein.</p>",
            missed: "<p><b>Blauen Bildschirm verpasst?</b> Ludora startet nicht, solange Secure Boot eingeschaltet ist. Schalten Sie Secure Boot in den Firmware-Einstellungen aus, starten Sie Ludora, führen Sie <tt>sudo ludora-secureboot setup</tt> aus, starten Sie neu, schließen Sie den blauen Bildschirm ab und schalten Sie Secure Boot dann wieder ein.</p>"
        },
        "fr": {
            offTitle: "Secure Boot",
            offBody: "<p>Secure Boot est <b>désactivé</b> sur ce PC, il n'y a donc rien à faire ici. Cliquez sur <b>Suivant</b>.</p><p>Si vous activez Secure Boot plus tard, lancez d'abord <tt>sudo ludora-secureboot setup</tt> dans Ludora et suivez ses instructions, puis activez-le.</p>",
            onTitle: "Secure Boot est activé : une étape de plus au premier démarrage",
            intro: "<p>Le noyau gaming de Ludora n'est pas signé par Microsoft. L'installateur crée donc une clé de signature pour ce PC. Votre PC doit approuver cette clé <b>une seule fois</b>, au premier démarrage après l'installation.</p>",
            lead: "<p>Lors de ce premier démarrage, un <b>écran bleu</b> apparaît. Procédez ainsi :</p>",
            steps: [
                "Lorsque <i>Press any key to perform MOK management</i> s'affiche, appuyez sur une touche <b>dans les 10 secondes</b>.",
                "Choisissez <b>Enroll MOK</b>.",
                "Choisissez <b>Continue</b>.",
                "Choisissez <b>Yes</b>.",
                "Tapez le mot de passe <b>ludora</b> et appuyez sur Entrée. Rien ne s'affiche pendant la saisie.",
                "Choisissez <b>Reboot</b>. Ludora démarre ensuite normalement, désormais sans cet écran."
            ],
            keyboard: "<p>L'écran bleu utilise une disposition de clavier américaine (QWERTY). Sur un clavier AZERTY, tapez la dernière lettre de <b>ludora</b> avec la touche <b>Q</b> : vous tapez donc <b>ludorq</b>.</p>",
            missed: "<p><b>Vous avez manqué l'écran bleu ?</b> Ludora ne démarre pas tant que Secure Boot est activé. Désactivez Secure Boot dans les paramètres du firmware, démarrez Ludora, lancez <tt>sudo ludora-secureboot setup</tt>, redémarrez, terminez l'écran bleu, puis réactivez Secure Boot.</p>"
        },
        "es": {
            offTitle: "Secure Boot",
            offBody: "<p>Secure Boot está <b>desactivado</b> en este PC, así que aquí no hay nada que hacer. Haz clic en <b>Siguiente</b>.</p><p>Si activas Secure Boot más adelante, ejecuta primero <tt>sudo ludora-secureboot setup</tt> en Ludora y sigue sus instrucciones; después actívalo.</p>",
            onTitle: "Secure Boot está activado: un paso más en el primer arranque",
            intro: "<p>El kernel gaming de Ludora no está firmado por Microsoft, así que el instalador crea una clave de firma para este PC. Tu PC tiene que aprobar esa clave <b>una sola vez</b>, la primera vez que arranque tras la instalación.</p>",
            lead: "<p>En ese primer arranque aparece una <b>pantalla azul</b>. Haz lo siguiente:</p>",
            steps: [
                "Cuando aparezca <i>Press any key to perform MOK management</i>, pulsa una tecla <b>en menos de 10 segundos</b>.",
                "Elige <b>Enroll MOK</b>.",
                "Elige <b>Continue</b>.",
                "Elige <b>Yes</b>.",
                "Escribe la contraseña <b>ludora</b> y pulsa Intro. No se muestra nada mientras escribes.",
                "Elige <b>Reboot</b>. Ludora arrancará con normalidad, a partir de ahora sin esta pantalla."
            ],
            keyboard: "<p>La pantalla azul usa la distribución de teclado de EE. UU. En un teclado AZERTY (p. ej. francés), escribe la última letra de <b>ludora</b> con la tecla <b>Q</b>.</p>",
            missed: "<p><b>¿Te saltaste la pantalla azul?</b> Ludora no arranca mientras Secure Boot esté activado. Desactiva Secure Boot en la configuración del firmware, arranca Ludora, ejecuta <tt>sudo ludora-secureboot setup</tt>, reinicia, completa la pantalla azul y vuelve a activar Secure Boot.</p>"
        },
        "it": {
            offTitle: "Secure Boot",
            offBody: "<p>Secure Boot è <b>disattivato</b> su questo PC, quindi qui non c'è nulla da fare. Fai clic su <b>Avanti</b>.</p><p>Se in seguito attivi Secure Boot, esegui prima <tt>sudo ludora-secureboot setup</tt> in Ludora e segui le istruzioni, poi attivalo.</p>",
            onTitle: "Secure Boot è attivo: un passaggio in più al primo avvio",
            intro: "<p>Il kernel gaming di Ludora non è firmato da Microsoft, quindi il programma di installazione crea una chiave di firma per questo PC. Il PC deve approvare questa chiave <b>una sola volta</b>, al primo avvio dopo l'installazione.</p>",
            lead: "<p>A quel primo avvio compare una <b>schermata blu</b>. Procedi così:</p>",
            steps: [
                "Quando compare <i>Press any key to perform MOK management</i>, premi un tasto <b>entro 10 secondi</b>.",
                "Scegli <b>Enroll MOK</b>.",
                "Scegli <b>Continue</b>.",
                "Scegli <b>Yes</b>.",
                "Digita la password <b>ludora</b> e premi Invio. Durante la digitazione non viene mostrato nulla.",
                "Scegli <b>Reboot</b>. Ludora si avvierà normalmente, d'ora in poi senza questa schermata."
            ],
            keyboard: "<p>La schermata blu usa il layout di tastiera statunitense. Su una tastiera AZERTY (ad es. francese), digita l'ultima lettera di <b>ludora</b> con il tasto <b>Q</b>.</p>",
            missed: "<p><b>Hai perso la schermata blu?</b> Ludora non si avvia finché Secure Boot è attivo. Disattiva Secure Boot nelle impostazioni del firmware, avvia Ludora, esegui <tt>sudo ludora-secureboot setup</tt>, riavvia, completa la schermata blu e poi riattiva Secure Boot.</p>"
        },
        "pt": {
            offTitle: "Secure Boot",
            offBody: "<p>O Secure Boot está <b>desativado</b> neste PC, por isso não há nada a fazer aqui. Pode avançar para o passo seguinte.</p><p>Se ativar o Secure Boot mais tarde, execute primeiro <tt>sudo ludora-secureboot setup</tt> no Ludora e siga as instruções; depois ative-o.</p>",
            onTitle: "O Secure Boot está ativado: um passo extra no primeiro arranque",
            intro: "<p>O kernel gaming do Ludora não é assinado pela Microsoft, por isso o instalador cria uma chave de assinatura para este PC. O seu PC tem de aprovar essa chave <b>uma única vez</b>, no primeiro arranque após a instalação.</p>",
            lead: "<p>Nesse primeiro arranque aparece um <b>ecrã azul</b>. Faça o seguinte:</p>",
            steps: [
                "Quando aparecer <i>Press any key to perform MOK management</i>, prima uma tecla <b>dentro de 10 segundos</b>.",
                "Escolha <b>Enroll MOK</b>.",
                "Escolha <b>Continue</b>.",
                "Escolha <b>Yes</b>.",
                "Escreva a palavra-passe <b>ludora</b> e prima Enter. Nada é mostrado enquanto escreve.",
                "Escolha <b>Reboot</b>. O Ludora passa a arrancar normalmente, a partir de agora sem este ecrã."
            ],
            keyboard: "<p>O ecrã azul usa o esquema de teclado dos EUA. Num teclado AZERTY (por ex. francês), escreva a última letra de <b>ludora</b> com a tecla <b>Q</b>.</p>",
            missed: "<p><b>Perdeu o ecrã azul?</b> O Ludora não arranca enquanto o Secure Boot estiver ativado. Desative o Secure Boot nas definições do firmware, arranque o Ludora, execute <tt>sudo ludora-secureboot setup</tt>, reinicie, conclua o ecrã azul e volte a ativar o Secure Boot.</p>"
        },
        "zh_CN": {
            offTitle: "安全启动",
            offBody: "<p>此电脑的安全启动（Secure Boot）已<b>关闭</b>，此处无需任何操作。请点击<b>下一步</b>。</p><p>如果以后要开启安全启动，请先在 Ludora 中运行 <tt>sudo ludora-secureboot setup</tt> 并按提示操作，然后再开启。</p>",
            onTitle: "安全启动已开启：首次启动时需要多做一步",
            intro: "<p>Ludora 的游戏内核没有经过微软签名，因此安装程序会为这台电脑创建一个签名密钥。安装完成后首次启动时，您的电脑需要确认这个密钥，<b>只需一次</b>。</p>",
            lead: "<p>首次启动时会出现一个<b>蓝色界面</b>。请按以下步骤操作：</p>",
            steps: [
                "出现 <i>Press any key to perform MOK management</i> 时，请在 <b>10 秒内</b>按任意键。",
                "选择 <b>Enroll MOK</b>。",
                "选择 <b>Continue</b>。",
                "选择 <b>Yes</b>。",
                "输入密码 <b>ludora</b> 并按回车键。输入时屏幕上不会显示任何内容。",
                "选择 <b>Reboot</b>。之后 Ludora 将正常启动，不会再出现此界面。"
            ],
            keyboard: "<p>蓝色界面使用美式键盘布局。如果使用 AZERTY 键盘（如法语键盘），请用 <b>Q</b> 键输入 <b>ludora</b> 的最后一个字母。</p>",
            missed: "<p><b>错过了蓝色界面？</b>安全启动开启时 Ludora 无法启动。请在固件设置中关闭安全启动，启动 Ludora，运行 <tt>sudo ludora-secureboot setup</tt>，重启并完成蓝色界面中的步骤，然后重新开启安全启动。</p>"
        },
        "ja": {
            offTitle: "セキュアブート",
            offBody: "<p>この PC ではセキュアブートが<b>無効</b>になっているため、ここで行うことはありません。<b>次へ</b>をクリックしてください。</p><p>後でセキュアブートを有効にする場合は、先に Ludora で <tt>sudo ludora-secureboot setup</tt> を実行して指示に従ってから有効にしてください。</p>",
            onTitle: "セキュアブートが有効です：初回起動時に手順が 1 つ増えます",
            intro: "<p>Ludora のゲーミングカーネルは Microsoft の署名を受けていないため、インストーラーがこの PC 用の署名鍵を作成します。インストール後の初回起動時に、この鍵を<b>一度だけ</b>承認する必要があります。</p>",
            lead: "<p>初回起動時に<b>青い画面</b>が表示されます。次の手順に従ってください：</p>",
            steps: [
                "<i>Press any key to perform MOK management</i> と表示されたら、<b>10 秒以内</b>に何かキーを押します。",
                "<b>Enroll MOK</b> を選択します。",
                "<b>Continue</b> を選択します。",
                "<b>Yes</b> を選択します。",
                "パスワード <b>ludora</b> を入力して Enter キーを押します。入力中は何も表示されません。",
                "<b>Reboot</b> を選択します。以後、Ludora はこの画面なしで通常どおり起動します。"
            ],
            keyboard: "<p>青い画面では US キーボード配列が使われます。AZERTY キーボード（フランス語など）では、<b>ludora</b> の最後の文字を <b>Q</b> キーで入力してください。</p>",
            missed: "<p><b>青い画面を見逃した場合：</b>セキュアブートが有効なままでは Ludora は起動しません。ファームウェア設定でセキュアブートを無効にして Ludora を起動し、<tt>sudo ludora-secureboot setup</tt> を実行して再起動し、青い画面の手順を完了してから、セキュアブートを再び有効にしてください。</p>"
        },
        "ko": {
            offTitle: "보안 부팅",
            offBody: "<p>이 PC에서는 보안 부팅(Secure Boot)이 <b>꺼져</b> 있으므로 여기서 할 일은 없습니다. <b>다음</b>을 누르세요.</p><p>나중에 보안 부팅을 켜려면 먼저 Ludora에서 <tt>sudo ludora-secureboot setup</tt>을 실행하고 안내에 따른 다음 켜세요.</p>",
            onTitle: "보안 부팅이 켜져 있음: 첫 부팅 시 한 단계가 더 있습니다",
            intro: "<p>Ludora의 게이밍 커널은 Microsoft의 서명을 받지 않았기 때문에, 설치 프로그램이 이 PC용 서명 키를 만듭니다. 설치 후 처음 부팅할 때 PC에서 이 키를 <b>한 번만</b> 승인해야 합니다.</p>",
            lead: "<p>첫 부팅 시 <b>파란 화면</b>이 나타납니다. 다음과 같이 하세요:</p>",
            steps: [
                "<i>Press any key to perform MOK management</i>가 표시되면 <b>10초 이내에</b> 아무 키나 누르세요.",
                "<b>Enroll MOK</b>을 선택하세요.",
                "<b>Continue</b>를 선택하세요.",
                "<b>Yes</b>를 선택하세요.",
                "비밀번호 <b>ludora</b>를 입력하고 Enter 키를 누르세요. 입력하는 동안 아무것도 표시되지 않습니다.",
                "<b>Reboot</b>를 선택하세요. 이후로는 이 화면 없이 Ludora가 정상적으로 시작됩니다."
            ],
            keyboard: "<p>파란 화면은 미국식 키보드 배열을 사용합니다. AZERTY 키보드(예: 프랑스어)에서는 <b>ludora</b>의 마지막 글자를 <b>Q</b> 키로 입력하세요.</p>",
            missed: "<p><b>파란 화면을 놓쳤나요?</b> 보안 부팅이 켜져 있는 동안에는 Ludora가 시작되지 않습니다. 펌웨어 설정에서 보안 부팅을 끄고 Ludora를 시작한 뒤 <tt>sudo ludora-secureboot setup</tt>을 실행하고, 다시 시작하여 파란 화면의 단계를 마친 다음 보안 부팅을 다시 켜세요.</p>"
        },
        "pl": {
            offTitle: "Secure Boot",
            offBody: "<p>Secure Boot jest na tym komputerze <b>wyłączony</b>, więc nie trzeba tu nic robić. Kliknij <b>Dalej</b>.</p><p>Jeśli później włączysz Secure Boot, najpierw uruchom w Ludorze <tt>sudo ludora-secureboot setup</tt> i postępuj zgodnie z instrukcjami, a dopiero potem go włącz.</p>",
            onTitle: "Secure Boot jest włączony: jeden dodatkowy krok przy pierwszym uruchomieniu",
            intro: "<p>Jądro gamingowe Ludory nie jest podpisane przez Microsoft, dlatego instalator tworzy klucz podpisu dla tego komputera. Komputer musi zatwierdzić ten klucz <b>jeden raz</b>, przy pierwszym uruchomieniu po instalacji.</p>",
            lead: "<p>Przy tym pierwszym uruchomieniu pojawi się <b>niebieski ekran</b>. Zrób tak:</p>",
            steps: [
                "Gdy pojawi się <i>Press any key to perform MOK management</i>, naciśnij dowolny klawisz <b>w ciągu 10 sekund</b>.",
                "Wybierz <b>Enroll MOK</b>.",
                "Wybierz <b>Continue</b>.",
                "Wybierz <b>Yes</b>.",
                "Wpisz hasło <b>ludora</b> i naciśnij Enter. Podczas wpisywania nic nie jest wyświetlane.",
                "Wybierz <b>Reboot</b>. Ludora uruchomi się normalnie, od teraz bez tego ekranu."
            ],
            keyboard: "<p>Niebieski ekran używa amerykańskiego układu klawiatury. Na klawiaturze AZERTY (np. francuskiej) wpisz ostatnią literę słowa <b>ludora</b> klawiszem <b>Q</b>.</p>",
            missed: "<p><b>Niebieski ekran został pominięty?</b> Ludora nie uruchomi się, dopóki Secure Boot jest włączony. Wyłącz Secure Boot w ustawieniach firmware, uruchom Ludorę, wykonaj <tt>sudo ludora-secureboot setup</tt>, uruchom komputer ponownie, przejdź przez niebieski ekran, a potem znów włącz Secure Boot.</p>"
        },
        "nl": {
            offTitle: "Secure Boot",
            offBody: "<p>Secure Boot staat op deze pc <b>uit</b>, dus hier hoeft niets te gebeuren. Klik op <b>Volgende</b>.</p><p>Zet je Secure Boot later aan, voer dan eerst <tt>sudo ludora-secureboot setup</tt> uit in Ludora en volg de instructies; zet het daarna pas aan.</p>",
            onTitle: "Secure Boot staat aan: één extra stap bij de eerste start",
            intro: "<p>De gamingkernel van Ludora is niet door Microsoft ondertekend. Daarom maakt het installatieprogramma een ondertekeningssleutel voor deze pc. Je pc moet die sleutel <b>één keer</b> goedkeuren, de eerste keer dat hij na de installatie opstart.</p>",
            lead: "<p>Bij die eerste start verschijnt een <b>blauw scherm</b>. Doe het volgende:</p>",
            steps: [
                "Als <i>Press any key to perform MOK management</i> verschijnt, druk dan <b>binnen 10 seconden</b> op een toets.",
                "Kies <b>Enroll MOK</b>.",
                "Kies <b>Continue</b>.",
                "Kies <b>Yes</b>.",
                "Typ het wachtwoord <b>ludora</b> en druk op Enter. Tijdens het typen wordt niets getoond.",
                "Kies <b>Reboot</b>. Ludora start daarna normaal op, voortaan zonder dit scherm."
            ],
            keyboard: "<p>Het blauwe scherm gebruikt een Amerikaanse toetsenbordindeling. Op een AZERTY-toetsenbord (bijv. Belgisch of Frans) typ je de laatste letter van <b>ludora</b> met de toets <b>Q</b>.</p>",
            missed: "<p><b>Blauw scherm gemist?</b> Ludora start niet zolang Secure Boot aan staat. Zet Secure Boot uit in de firmware-instellingen, start Ludora, voer <tt>sudo ludora-secureboot setup</tt> uit, herstart, doorloop het blauwe scherm en zet Secure Boot daarna weer aan.</p>"
        },
        "da": {
            offTitle: "Secure Boot",
            offBody: "<p>Secure Boot er <b>slået fra</b> på denne pc, så der er intet at gøre her. Klik på <b>Næste</b>.</p><p>Hvis du slår Secure Boot til senere, så kør først <tt>sudo ludora-secureboot setup</tt> i Ludora og følg vejledningen, og slå det derefter til.</p>",
            onTitle: "Secure Boot er slået til: ét ekstra trin ved første opstart",
            intro: "<p>Ludoras gaming-kerne er ikke signeret af Microsoft, så installationsprogrammet opretter en signeringsnøgle til denne pc. Din pc skal godkende nøglen <b>én gang</b>, første gang den starter efter installationen.</p>",
            lead: "<p>Ved den første opstart vises en <b>blå skærm</b>. Gør sådan:</p>",
            steps: [
                "Når der står <i>Press any key to perform MOK management</i>, så tryk på en tast <b>inden for 10 sekunder</b>.",
                "Vælg <b>Enroll MOK</b>.",
                "Vælg <b>Continue</b>.",
                "Vælg <b>Yes</b>.",
                "Skriv adgangskoden <b>ludora</b>, og tryk på Enter. Der vises intet, mens du skriver.",
                "Vælg <b>Reboot</b>. Ludora starter derefter normalt, fremover uden denne skærm."
            ],
            keyboard: "<p>Den blå skærm bruger et amerikansk tastaturlayout. På et AZERTY-tastatur (f.eks. fransk) skriver du det sidste bogstav i <b>ludora</b> med <b>Q</b>-tasten.</p>",
            missed: "<p><b>Gik du glip af den blå skærm?</b> Ludora starter ikke, så længe Secure Boot er slået til. Slå Secure Boot fra i firmwareindstillingerne, start Ludora, kør <tt>sudo ludora-secureboot setup</tt>, genstart, gennemfør den blå skærm, og slå så Secure Boot til igen.</p>"
        },
        "fi": {
            offTitle: "Secure Boot",
            offBody: "<p>Secure Boot on tässä tietokoneessa <b>pois päältä</b>, joten tässä ei tarvitse tehdä mitään. Napsauta <b>Seuraava</b>.</p><p>Jos otat Secure Bootin myöhemmin käyttöön, suorita ensin Ludorassa <tt>sudo ludora-secureboot setup</tt> ja noudata ohjeita, ja ota se vasta sitten käyttöön.</p>",
            onTitle: "Secure Boot on käytössä: yksi lisävaihe ensimmäisellä käynnistyskerralla",
            intro: "<p>Ludoran pelikäyttöön tehtyä ydintä ei ole allekirjoittanut Microsoft, joten asennusohjelma luo tälle tietokoneelle allekirjoitusavaimen. Tietokoneen täytyy hyväksyä avain <b>kerran</b>, kun se käynnistyy ensimmäisen kerran asennuksen jälkeen.</p>",
            lead: "<p>Ensimmäisellä käynnistyskerralla näkyviin tulee <b>sininen näyttö</b>. Toimi näin:</p>",
            steps: [
                "Kun näytössä lukee <i>Press any key to perform MOK management</i>, paina mitä tahansa näppäintä <b>10 sekunnin kuluessa</b>.",
                "Valitse <b>Enroll MOK</b>.",
                "Valitse <b>Continue</b>.",
                "Valitse <b>Yes</b>.",
                "Kirjoita salasana <b>ludora</b> ja paina Enter. Kirjoittaessa mitään ei näytetä.",
                "Valitse <b>Reboot</b>. Ludora käynnistyy sen jälkeen normaalisti, tästä lähtien ilman tätä näyttöä."
            ],
            keyboard: "<p>Sininen näyttö käyttää yhdysvaltalaista näppäimistöasettelua. AZERTY-näppäimistöllä (esim. ranskalaisella) kirjoita sanan <b>ludora</b> viimeinen kirjain <b>Q</b>-näppäimellä.</p>",
            missed: "<p><b>Menikö sininen näyttö ohi?</b> Ludora ei käynnisty, kun Secure Boot on käytössä. Poista Secure Boot käytöstä laiteohjelmiston asetuksista, käynnistä Ludora, suorita <tt>sudo ludora-secureboot setup</tt>, käynnistä uudelleen, käy sininen näyttö läpi ja ota Secure Boot sitten taas käyttöön.</p>"
        },
        "nb": {
            offTitle: "Secure Boot",
            offBody: "<p>Secure Boot er <b>slått av</b> på denne PC-en, så det er ingenting å gjøre her. Klikk på <b>Neste</b>.</p><p>Hvis du slår på Secure Boot senere, kjør først <tt>sudo ludora-secureboot setup</tt> i Ludora og følg instruksjonene, og slå det deretter på.</p>",
            onTitle: "Secure Boot er slått på: ett ekstra steg ved første oppstart",
            intro: "<p>Ludoras spillkjerne er ikke signert av Microsoft, så installasjonsprogrammet lager en signeringsnøkkel for denne PC-en. PC-en må godkjenne nøkkelen <b>én gang</b>, første gang den starter etter installasjonen.</p>",
            lead: "<p>Ved den første oppstarten vises en <b>blå skjerm</b>. Gjør slik:</p>",
            steps: [
                "Når det står <i>Press any key to perform MOK management</i>, trykk på en tast <b>innen 10 sekunder</b>.",
                "Velg <b>Enroll MOK</b>.",
                "Velg <b>Continue</b>.",
                "Velg <b>Yes</b>.",
                "Skriv inn passordet <b>ludora</b> og trykk Enter. Ingenting vises mens du skriver.",
                "Velg <b>Reboot</b>. Ludora starter deretter som normalt, heretter uten denne skjermen."
            ],
            keyboard: "<p>Den blå skjermen bruker amerikansk tastaturoppsett. På et AZERTY-tastatur (f.eks. fransk) skriver du den siste bokstaven i <b>ludora</b> med <b>Q</b>-tasten.</p>",
            missed: "<p><b>Gikk du glipp av den blå skjermen?</b> Ludora starter ikke så lenge Secure Boot er slått på. Slå av Secure Boot i fastvareinnstillingene, start Ludora, kjør <tt>sudo ludora-secureboot setup</tt>, start på nytt, fullfør den blå skjermen og slå deretter Secure Boot på igjen.</p>"
        },
        "sv": {
            offTitle: "Secure Boot",
            offBody: "<p>Secure Boot är <b>avstängt</b> på den här datorn, så här finns inget att göra. Klicka på <b>Nästa</b>.</p><p>Om du slår på Secure Boot senare, kör först <tt>sudo ludora-secureboot setup</tt> i Ludora och följ instruktionerna, och slå sedan på det.</p>",
            onTitle: "Secure Boot är påslaget: ett extra steg vid första starten",
            intro: "<p>Ludoras spelkärna är inte signerad av Microsoft, så installationsprogrammet skapar en signeringsnyckel för den här datorn. Datorn måste godkänna nyckeln <b>en gång</b>, första gången den startar efter installationen.</p>",
            lead: "<p>Vid den första starten visas en <b>blå skärm</b>. Gör så här:</p>",
            steps: [
                "När det står <i>Press any key to perform MOK management</i>, tryck på en tangent <b>inom 10 sekunder</b>.",
                "Välj <b>Enroll MOK</b>.",
                "Välj <b>Continue</b>.",
                "Välj <b>Yes</b>.",
                "Skriv lösenordet <b>ludora</b> och tryck på Enter. Inget visas medan du skriver.",
                "Välj <b>Reboot</b>. Ludora startar sedan som vanligt, hädanefter utan den här skärmen."
            ],
            keyboard: "<p>Den blå skärmen använder amerikansk tangentbordslayout. På ett AZERTY-tangentbord (t.ex. franskt) skriver du sista bokstaven i <b>ludora</b> med <b>Q</b>-tangenten.</p>",
            missed: "<p><b>Missade du den blå skärmen?</b> Ludora startar inte så länge Secure Boot är påslaget. Stäng av Secure Boot i firmwareinställningarna, starta Ludora, kör <tt>sudo ludora-secureboot setup</tt>, starta om, slutför den blå skärmen och slå sedan på Secure Boot igen.</p>"
        }
    })

    ScrollView {
        anchors.fill: parent
        anchors.margins: 12
        contentWidth: availableWidth

        Label {
            width: parent.width
            wrapMode: Text.WordWrap
            textFormat: Text.RichText
            font.pointSize: 12
            text: page.html(page.texts[page.lang])
        }
    }
}
